# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrianglePlugin
                                 A QGIS plugin
 Triangles a mesh
                             -------------------
        begin                : 2014-05-27
        copyright            : (C) 2014 by Sergio Villarroel
        email                : svillarr@dcc.uchile.cl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load TrianglePlugin class from file TrianglePlugin
    from triangleplugin import TrianglePlugin
    return TrianglePlugin(iface)
