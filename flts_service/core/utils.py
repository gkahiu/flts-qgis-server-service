# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FltsUtils
Description          : FLTS service utils
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
import json
from typing import Dict

from qgis.server import QgsServerResponse


def write_json_response(
        data:Dict[str, str],
        response: QgsServerResponse,
        code: int=200
) -> None:
    # Output server response to JSON
    response.setStatusCode(code)
    response.setHeader('Content-Type', 'application/json')
    response.write(json.dumps(data))