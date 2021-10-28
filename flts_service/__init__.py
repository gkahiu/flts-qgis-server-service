# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : FLTSServerPlugin
Description          : Plugin for adding Qr Code and barcode layout in a print
                       layout
Date                 : 24-10-2021
copyright            : (C) 2021 by John Gitau
                       See the accompanying file CONTRIBUTORS.txt in the root
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


# noinspection PyPep8Naming
def serverClassFactory(iface):  # pylint: disable=invalid-name
    """Load the plugin loader class

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from flts_service.plugin import FltsServicePluginLoader
    return FltsServicePluginLoader(iface)