# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TrianglePluginDialog
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
"""

from PyQt4 import QtCore, QtGui
from ui_triangleplugin import Ui_TrianglePlugin
from qgis.core import QgsMapLayerRegistry,QgsMapLayer
from shapeDescriptors import *

class TrianglePluginDialog(QtGui.QDialog, Ui_TrianglePlugin):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        #Building the shape descriptor's combobox
        self.cbShapeDescriptor.addItem("No Shape Descriptor", lambda p,t: funNoShapeDescriptor(p,t))
        self.cbShapeDescriptor.addItem("Form Factor",lambda p,t: funFormFactor(p,t))
        self.cbShapeDescriptor.addItem("Compact",lambda p,t: funCompact(p,t))
        self.cbShapeDescriptor.addItem("Solidity Index",lambda p,t: funSolidityIndex(p,t))
        self.cbShapeDescriptor.addItem("Convexity Index",lambda p,t: funConvexityIndex(p,t))
        
    def populateCombobox(self):
        #Populates the comboboxes in the dialog.
        #It must be called when the plugin is required (that's why is not build in the initialization 
        self.clear()
        layers=QgsMapLayerRegistry.instance().mapLayers().values()
        for layer in layers:
            if layer.type()== QgsMapLayer.VectorLayer:
                self.cbLayers.addItem(layer.name(),layer)
        self.cbLayers.setCurrentIndex(-1)
        
    def clear(self):
        self.cbLayers.clear()
        self.textAngle.clear()
        self.textArea.clear()
        self.textName.clear()
    