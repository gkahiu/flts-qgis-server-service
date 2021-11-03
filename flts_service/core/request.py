# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FltsServerRequest
Description          : Provides additional attributes specific to the FLTS
                       request.
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
from qgis.server import QgsServerRequest

from flts_service.core.exception import FltsServiceException


class FltsServerRequest(QgsServerRequest):
    """Provides access to additional attributes for request to the FLTS
    service.
    """
    # Enums for processing one template or all
    FIRST, ALL, NOT_DEFINED = range(0, 3)

    @property
    def request(self) -> str:
        """Request from parameters, can be for starter title, land hold
        title, reports etc.
        """
        return self.parameters().get('REQUEST', '').lower()

    @property
    def template_id(self) -> str:
        """Returns the template_id specified in the request. This is case
        sensitive.
        """
        return self.parameters().get('TEMPLATE_ID', '')

    @property
    def query_count(self) -> int:
        """Returns an int indicating whether to process one record
        (whose output layout will be a PDF) or all records (whose
        output layouts will be zipped).
        """
        cnt_str = self.parameters().get('QUERY', '').lower()

        # Default value
        cnt_int = FltsServerRequest.NOT_DEFINED

        try:
            cnt = int(cnt_str)
            # Set to FIRST or ALL if outside range
            if cnt >= 0 or cnt < 2:
                cnt_int = cnt
        except ValueError:
            raise FltsServiceException(
                400,
                'Invalid QUERY parameter. Use 0 for FIRST or 1 for ALL.'
            )

        return cnt_int
