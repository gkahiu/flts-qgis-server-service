# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FltsServicePluginLoader
Description          : Loader for the demo FLTS QGIS Server service.
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
from qgis.core import Qgis, QgsMessageLog
from flts_service.core.service import FltsService


class FltsServicePluginLoader:
    """QGIS Server plugin loader."""

    def __init__(self, server_iface):
        """Constructor.

        :param server_iface: An interface instance that exposes the QGIS
        server interface.
        :type server_iface: QgsServerInterface
        """
        # Register FLTS custom service
        server_iface.serviceRegistry().registerService(
            FltsService(server_iface)
        )
        QgsMessageLog.logMessage("Demo FLTS Service registered", 'flts', Qgis.Info)


