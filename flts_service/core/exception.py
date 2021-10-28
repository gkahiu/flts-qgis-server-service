# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FltsServiceException
Description          : Service exception to be sent back to the client.
Date                 : 26-10-2021
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
from qgis.core import (
    Qgis,
    QgsMessageLog
)
from qgis.server import QgsServerResponse

from flts_service.core.utils import (
    write_json_response
)


class FltsServiceException(Exception):
    """Write exception to server response in JSON format.
    """

    def __init__(self, code: int, msg: str):
        super().__init__(msg)
        self.code = code
        self.msg = msg
        QgsMessageLog.logMessage(
            'FLTS service error {0}: {1}'.format(code, msg),
            level=Qgis.Critical
        )

    def formatResponse(self, response: QgsServerResponse):
        # Write exception to response object
        body = {'status': 'error', 'message': self.msg}
        response.clear()
        write_json_response(body, response, self.code)