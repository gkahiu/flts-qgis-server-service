# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FltsService
Description          : Service for handling FLTS service.
Date                 : 24-10-2021
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
import traceback

from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsProject
)
from qgis.PyQt.QtCore import (
    QDateTime,
    QDir,
    QFile,
    QTemporaryFile
)
from qgis.server import (
    QgsServerRequest,
    QgsServerResponse,
    QgsService
)
from flts_service.core.handlers import BaseRequestHandler
from flts_service.core.request import FltsServerRequest
from flts_service.core.exception import FltsServiceException


class FltsService(QgsService):
    """Service for handling FLTS service.
    """

    def __init__(self, server_iface):
        super().__init__()
        self._iface = server_iface
        self._handlers = dict()
        self._init()

    def _init(self):
        # Register request handlers and index by request_id
        handlers_cls = BaseRequestHandler.handlers
        for h in handlers_cls:
            self._handlers[h.REQUEST_ID.lower()] = h(self._iface, self)

    @property
    def iface(self):
        """
        :return: Returns an instance of the server interface.
        :rtype: QgsServerInterface
        """
        return self._iface

    def name(self):
        """
        :return: Service name also used as query parameter.
        :rtype: str
        """
        return 'FLTS'

    def version(self):
        """
        :return: Service version
        :rtype: str
        """
        return '1.0.0'

    def executeRequest(
            self,
            request: QgsServerRequest,
            response: QgsServerResponse,
            project: QgsProject
    ):
        # Handle requests sent to the 'FLTS' service
        try:
            flts_req = FltsServerRequest(request)
            req_str = flts_req.request
            if not req_str:
                raise FltsServiceException(
                    400,
                    'Null REQUEST parameter'
                )

            handler = self._handlers.get(req_str.lower())
            if handler is None:
                raise FltsServiceException(
                    400,
                    '\'{0}\' is an invalid REQUEST parameter. Must be '
                    'GetStarterCert, xyz or abc'.format(req_str)
                )
            else:
                # Handover request to the handler
                handler.exec_request(flts_req, response)

        except FltsServiceException as fex:
            fex.formatResponse(response)

        except Exception:
            code=500
            QgsMessageLog.logMessage(
                'FLTS service error {0}: {1}'.format(
                    code,
                    traceback.format_exc()
                ),
                level=Qgis.Critical
            )
            err = FltsServiceException(code, 'Internal FLTS service error')
            err.formatResponse(response)

