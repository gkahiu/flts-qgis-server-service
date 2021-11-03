# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Renderer
Description          : Renderer for FLTS requests
Date                 : 02-11-2021
copyright            : (C) 2021 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from typing import (
    Union,
    Tuple
)

from qgis.PyQt.QtCore import (
    QDateTime,
    QDir,
    QFile,
    QTemporaryFile
)
from qgis.core import (
    Qgis,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsMessageLog,
    QgsProject
)

from flts_service.core.exception import FltsServiceException


class RendererContext:
    """Provides context settings for the renderer.
    """
    # Document file naming convention - use record_id or auto-generate (UUID)
    REC_ID, AUTO_GEN = range(0, 2)

    def __init__(
            self,
            project: Union[QgsProject, str],
            server_iface: 'QgsServerInterface'
    ):
        self._project = project
        if isinstance(self._project, str):
            self._project = RendererContext.project_from_path(self._project)

        self._server_iface = server_iface
        self._naming_conv = RendererContext.REC_ID

        # Assume there will be a default template named 'Main'
        self.layout_id = 'Main'
        self._item_values = {}

        # Some project properties that will be cascaded to the pdf file. See
        # QgsProjectMetadata for more options.
        self.proj_title = ''
        self.proj_author = 'FLTS Main Author'
        self.proj_abstract = ''

        # Update project metadata
        self.update_project_metadata()

        self.document_dir = ''

    @property
    def project(self) -> QgsProject:
        """Returns QGIS project object.
        """
        return self._project

    def update_project_metadata(self):
        # Update based on context properties
        md = self._project.metadata()
        md.setTitle(self.proj_title)
        md.setAuthor(self.proj_author)
        md.setCreationDateTime(QDateTime.currentDateTime())
        md.setAbstract(self.proj_abstract)
        self._project.setMetadata(md)

    @project.setter
    def project(self, project_path: str):
        """Set project from path.
        """
        self._project = RendererContext.project_from_path(project_path)
        self.update_project_metadata()

    @staticmethod
    def project_from_path(path: str) -> QgsProject:
        # Create project from the path.
        if not QFile.exists(path):
            raise FltsServiceException(
                404,
                'Project file \'{0}\' not found.'.format(path)
            )

        # Load project
        QgsProject.instance().read(path)

        return QgsProject.instance()

    @property
    def naming(self) -> int:
        """Naming convention for PDF document. Default is to use record_id.
        """
        return self._naming_conv

    @naming.setter
    def naming(self, conv: int):
        """Set document naming convention.
        """
        self._naming_conv = conv

    @property
    def item_values(self) -> dict:
        """Return dictionary containing item values with the key
        corresponding to the item id (in the layout) and value corresponding
        to the value (e.g. text for a label, layer for a map, file path for
        picture etc.
        """
        return self._item_values

    @item_values.setter
    def item_values(self, value_map: dict):
        """Set the item values collection. It overrides the previous
        collection.
        """
        self._item_values = value_map

    def append_item_value(self, item_id: str, value: object):
        """Specify value for a layout item with the given id. Previous value
        for the item will be overridden.
        """
        self._item_values[item_id] = value


class FltsRenderer:
    """Renders requests to the FLTS service.
    """

    def __init__(self, ctx: RendererContext):
        self._ctx = ctx
        self._ctx.update_project_metadata()

    @property
    def context(self) -> RendererContext:
        """Returns RendererContext used by this class.
        """
        return self._ctx

    def _get_layout(self):
        template_name = self._ctx.layout_id
        if not template_name:
            raise FltsServiceException(
                500,
                'Template name not specified.'
            )
        # Check template
        lyt_mgr = self._ctx.project.layoutManager()
        doc_layout = lyt_mgr.layoutByName(template_name)
        if not doc_layout:
            raise FltsServiceException(
                404,
                '\'{0}\' layout not found in the QGIS project file.'.format(
                    template_name
                )
            )
        # Layout should have at least one page
        if doc_layout.pageCollection().pageCount() < 1:
            raise FltsServiceException(
                500,
                'No pages in layout template.'.format(
                    template_name
                )
            )

        return doc_layout

    def _configure_layout(self, layout):
        """Set values for items in the layout. Currently only supports
        labels but should also incorporate maps, picture, legend items etc.
        """
        for item_id, value in self._ctx.item_values.items():
            item = layout.itemById(item_id)
            # Labels
            if isinstance(item, QgsLayoutItemLabel):
                # Handle non string data types. Need to incorporate checks
                # for complex types.
                if not isinstance(value, str):
                    value = str(value)
                item.setText(value)

    def get_document(self) -> Tuple[QgsLayoutExporter.ExportResult, QTemporaryFile]:
        """Generate document and return tuple containing export result
        (success, failure etc.) and temporary file containing the document
        if the result was success.
        """
        layout = self._get_layout()
        self._configure_layout(layout)

        # Write to temp file
        doc_dir = self._ctx.document_dir
        if not doc_dir:
            doc_dir = QDir.tempPath()
        temp_file = QTemporaryFile('{0}/XXXXXX.pdf'.format(doc_dir))
        if not temp_file.open():
            raise FltsServiceException(
                500,
                'Could not open temporary file to write document.'
            )

        # Write document to temp file
        settings = QgsLayoutExporter.PdfExportSettings()
        exporter = QgsLayoutExporter(layout)
        result = exporter.exportToPdf(temp_file.fileName(), settings)

        return result, temp_file
