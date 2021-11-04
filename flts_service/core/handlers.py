# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FltsRequestHandlers
Description          : Handlers for FLTS for specific service requests
Date                 : 25-10-2021
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
from dataclasses import dataclass
from collections import OrderedDict
from typing import Dict
from zipfile import ZipFile
from abc import (
    ABC,
    abstractmethod,
    abstractproperty
)

from qgis.PyQt.QtCore import (
    QDateTime,
    QDir,
    QFile,
    QIODevice,
    QTemporaryFile
)
from qgis.core import (
    Qgis,
    QgsLayoutExporter,
    QgsMessageLog
)
from qgis.server import (
    QgsServerInterface,
    QgsServerResponse
)

from flts_service.core.exception import FltsServiceException
from flts_service.core.renderer import (
    FltsRenderer,
    RendererContext
)
from flts_service.core.request import FltsServerRequest
from flts_service.core.utils import write_json_response


@dataclass
class ProjectInfo:
    """Mimic table structure for storing QGS project files and
    corresponding variable names and values.
    """
    id: str
    path: str
    variable_map: dict


def create_project_meta():
    """File paths to project files and corresponding metadata."""
    projects = {}

    # Mimic values from the db
    variable_map_1 = OrderedDict({
        '190865': {'lbl_first_name': 'Alex', 'lbl_last_name': 'Jones'},
        '569813': {'lbl_first_name': 'Tracy', 'lbl_last_name': 'Lee'}
    })

    variable_map_2 = OrderedDict({
        'Makongeni': {'lbl_county': 'Nairobi', 'lbl_constituency': 'Madaraka'},
        'Ichaweri': {'lbl_county': 'Kiambu', 'lbl_constituency': 'Gatundu South'}
    })

    p1 = ProjectInfo(
        'D4F9A1A4',
        'D:/xampp/apache/docs/sample1.qgs',
        variable_map_1
    )
    projects[p1.id] = p1

    p2 = ProjectInfo(
        '86AB5327',
        'D:/xampp/apache/docs/sample2.qgs',
        variable_map_2
    )
    projects[p2.id] = p2

    return projects


class BaseRequestHandler(ABC):
    """Provides common functionality across all request handlers.
    """
    # Should match request name handed over by server
    REQUEST_ID = ''

    # Used to exclude handler from being registered
    EXCLUDE_REGISTER_ID = 'BACKEND'

    # Container for registering sub-classes
    handlers = []

    def __init__(self, iface: QgsServerInterface, service: 'FltsService'):
        self._iface = iface
        self._service = service
        self._projects = create_project_meta()

    def __init_subclass__(cls, **kwargs):
        # Auto-register subclasses
        super().__init_subclass__(**kwargs)

        # Use REQUEST_ID as the key
        if not cls.REQUEST_ID:
            cls.log_error('Request ID missing to register sub-class.')
            raise FltsServiceException(
                500,
                'Internal server error'
            )
        if cls.REQUEST_ID != BaseRequestHandler.EXCLUDE_REGISTER_ID:
            BaseRequestHandler.handlers.append(cls)

    @property
    def server_iface(self) -> QgsServerInterface:
        """
        :return: Returns an instance of the server object that exposes QGIS
        Server interfaces.
        :rtype: QgsServerInterface
        """
        return self._iface

    @property
    def service(self) -> 'FltsService':
        """Returns a reference to the FltsService.
        """
        return self._service

    @classmethod
    def log_error(cls, msg: str):
        # Log error message
        QgsMessageLog.logMessage( msg, level=Qgis.Critical)

    @classmethod
    def log_info(cls, msg:str):
        # Log information message
        QgsMessageLog.logMessage(msg, level=Qgis.Info)

    @abstractmethod
    def exec_request(self, request: FltsServerRequest, response: 'QgsServerResponse'):
        """
        Execute request sent by our custom service. Base implementation does
        nothing, to be implemented by sub-classes.
        """
        pass


class AbstractDocumentRequestHandler(BaseRequestHandler):
    """For use by handlers that require document functionality.
    """
    REQUEST_ID = BaseRequestHandler.EXCLUDE_REGISTER_ID

    @abstractproperty
    def document_prefix(self) -> str:
        """Text to append before document file name. Abstract implementation
        returns an empty string.
        """
        return ''

    def create_archive(
            self,
            docs: Dict[str, QTemporaryFile],
            temp_dir: str
    ) -> str:
        # Zip the documents and name archive using current date/time
        archive_name = '{0}/{1}_archive_{2}.zip'.format(
            temp_dir,
            self.document_prefix,
            QDateTime.currentDateTime().toString('yyyyMMddhhmmss')
        )
        with ZipFile(archive_name, 'w') as archive:
            for file_name, temp_file in docs.items():
                archive.write(
                    temp_file.fileName(),
                    '{0}.pdf'.format(file_name)
                )

        return archive_name

    def project_by_id(self, temp_id: str) -> ProjectInfo:
        """
        Retrieves a ProjectInfo object, containing a QGS project object,
        based on specified ID registered in the our collection.
        """
        return self._projects.get(temp_id, None)

    def send_documents(
            self,
            docs: Dict[str, QTemporaryFile],
            response: QgsServerResponse,
            temp_dir: str
    ):
        # Package documents and send to the client
        num_docs = len(docs)
        if num_docs == 0:
            data = {'status': 'success', 'message': 'No documents processed'}
            write_json_response(data, response, 200)

        elif num_docs == 1:
            # Get first/only document in the collection
            file_name = list(docs)[0]
            doc = docs[file_name]
            response.setStatusCode(200)
            response.setHeader('Content-Type', 'application/pdf')
            response.write(doc.readAll())

        else:
            # Create archive
            archive_path = self.create_archive(docs, temp_dir)
            file = QFile(archive_path)
            if not file.exists():
                FltsServiceException(
                    500,
                    'Could not create document archive.'
                )
            if file.open(QIODevice.ReadOnly):
                response.setStatusCode(200)
                response.setHeader('Content-Type', 'application/zip')
                response.write(file.readAll())
            else:
                FltsServiceException(
                    500,
                    'Could not read document archive.'
                )


class CapabilitiesRequestHandler(BaseRequestHandler):
    """Exposes FLTS service capabilities.
    """
    REQUEST_ID = "GetCapabilities"

    def exec_request(
            self,
            request: FltsServerRequest,
            response: 'QgsServerResponse'
    ):
        # Sample capabilities
        info = {
            'Name': self.service.name(),
            'Version': self.service.version(),
            'Description': 'Demo service that currently supports starter title...',
            'Contact Person': 'John Gitau',
            'Contact Organization': 'xxxx yyyy'
        }
        write_json_response(info, response, 200)


class StarterRequestHandler(AbstractDocumentRequestHandler):
    """Demo handler for simulating generation of starter certificates.
    """
    REQUEST_ID = 'GetStarterCert'

    @property
    def document_prefix(self) -> str:
        """Appended to document or archive file names.
        """
        return 'Starter_Title'

    def renderer_context(self, info: ProjectInfo) -> RendererContext:
        """Create the context for using in the renderer.
        """
        ctx = RendererContext(info.path, self.server_iface)
        ctx.proj_title = 'Starter Title'
        ctx.proj_abstract = 'Document produced by FLTS starter title module'
        ctx.proj_author = 'CB-FLTS Document Author'
        ctx.layout_id = 'Main'

        return ctx

    def exec_request(
            self,
            request: FltsServerRequest,
            response: 'QgsServerResponse'
    ):
        template_id = request.template_id
        if not template_id:
            raise FltsServiceException(
                400,
                'Null TEMPLATE_ID parameter'
            )

        proj_info = self.project_by_id(template_id)
        if proj_info is None:
            raise FltsServiceException(
                400,
                '\'{0}\' is an invalid value for '
                'TEMPLATE_ID parameter'.format(template_id)
            )

        count_enum = request.query_count
        # Use FIRST to return first 'record' if enum is NOT_DEFINED
        if count_enum == FltsServerRequest.NOT_DEFINED:
            count_enum = FltsServerRequest.FIRST

        # Temp directory for documents
        doc_dir = QDir.tempPath()
        doc_files = {}
        for k, field_values in proj_info.variable_map.items():
            # Get context
            renderer_ctx = self.renderer_context(proj_info)
            renderer_ctx.document_dir = doc_dir
            renderer_ctx.item_values = field_values
            renderer = FltsRenderer(renderer_ctx)
            res, doc = renderer.get_document()
            if res == QgsLayoutExporter.Success:
                doc_files[k] = doc
                # Fetch only the first one if enum is set to FIRST
                if count_enum == FltsServerRequest.FIRST:
                    break
            else:
                self.log_error(
                    'Error {0} occurred while exporting layout to PDF'.format(
                        str(res)
                    )
                )

        # response.clear()
        self.send_documents(doc_files, response, doc_dir)

