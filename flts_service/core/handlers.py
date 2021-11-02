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

from qgis.PyQt.QtCore import (
    QByteArray,
    QFile
)
from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsProject
)
from qgis.server import (
    QgsServerInterface,
    QgsServerResponse
)

from flts_service.core.exception import FltsServiceException
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


class BaseRequestHandler:
    """Provides common functionality across all request handlers.
    """
    # Should match request name sent by server
    REQUEST_ID = ''

    # Container for registering sub-classes
    handlers = []

    def __init__(self, server_iface):
        self._iface = server_iface
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

        BaseRequestHandler.handlers.append(cls)

    @property
    def server_iface(self) -> QgsServerInterface:
        """
        :return: Returns an instance of the server object that exposes QGIS
        Server interfaces.
        :rtype: QgsServerInterface
        """
        return self._iface

    @classmethod
    def log_error(cls, msg: str):
        # Log error message
        QgsMessageLog.logMessage( msg, level=Qgis.Critical)

    @classmethod
    def log_info(cls, msg:str):
        # Log information message
        QgsMessageLog.logMessage(msg, level=Qgis.Info)

    def project_by_id(self, temp_id: str) -> ProjectInfo:
        """
        Retrieves a ProjectInfo object, containing a QGS project object,
        based on specified ID registered in the our collection.
        """
        return self._projects.get(temp_id, None)

    def send_docs(
            self,
            docs: list,
            response: QgsServerResponse
    ):
        """Write files to response using the given content type. If
        only one file in the list then the content type will be pdf.
        `docs` contains a list of QByteArray objects.
        """
        content_type = 'application/pdf'
        if len(docs) > 1:
            content_type = 'application/zip'

    def exec_request(
            self,
            request: FltsServerRequest,
            response: 'QgsServerResponse',
            service: 'QgsService'
    ):
        """
        Execute request sent by our custom service. Base implementation does
        nothing, to be implemented by sub-classes.
        """
        pass


def render_document(
        project_path: str,
        field_values: dict,
        request: FltsServerRequest,
        iface: QgsServerInterface,
        layout:str = 'Main'
) -> QByteArray:
    """Generate single document based on project file and values for
    corresponding fields/items in the layout.
    """
    # Check if the project file exists
    if not QFile.exists(project_path):
        raise FltsServiceException(
            404,
            'Layout template not found'
        )

    project = QgsProject.instance().read(project_path)

    # Inject custom parameters into WMS parameters object
    request.setParameter('MAP', project_path)
    request.setParameter('TEMPLATE', layout)
    for k, v in field_values.items():
        request.setParameter(k, v)

    wms_req = QgsWmsRequest(request)
    wms_params = wms_req.wmsParameters()

    wms_ctx = QgsWmsRenderContext(project, iface)
    wms_ctx.setParameters(wms_params)

    renderer = QgsRenderer(wms_ctx)

    return renderer.getPrint()


class CapabilitiesRequestHandler(BaseRequestHandler):
    """Exposes FLTS service capabilities.
    """
    REQUEST_ID = "GetCapabilities"

    def exec_request(
            self,
            request: FltsServerRequest,
            response: 'QgsServerResponse',
            service: 'QgsService'
    ):
        # Sample capabilities
        info = {
            'Name': service.name(),
            'Version': service.version(),
            'Description': 'Demo service for generating starter title...',
            'Contact Person': 'John Gitau',
            'Contact Organization': 'xxxx yyyy'
        }
        write_json_response(info, response, 200)


class StarterRequestHandler(BaseRequestHandler):
    """Demo handler for simulating generation of starter certificates.
    """
    REQUEST_ID = 'GetStarterCert'

    def exec_request(
            self,
            request: FltsServerRequest,
            response: 'QgsServerResponse',
            service: 'QgsService'
    ):
        # Generate starter title certificates
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

        vars = proj_info.variable_map
        i = 0
        docs = []
        for k, field_values in vars.items():
            ba = render_document(
                proj_info.path,
                field_values,
                request,
                self.server_iface
            )
            docs.append(ba)
            # Fetch only the first one if enum is set to FIRST
            if count_enum == FltsServerRequest.FIRST:
                break

