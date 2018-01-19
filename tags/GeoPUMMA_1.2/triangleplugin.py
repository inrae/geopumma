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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from triangleplugindialog import TrianglePluginDialog
import os.path
#Import classes
import meshpy.triangle as triangle
import numpy as np
from matplotlib.path import Path

class TrianglePlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'triangleplugin_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = TrianglePluginDialog()

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/triangleplugin/icon.png"),
            u"Triangle", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Triangle Plugin", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Triangle Plugin", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # show the dialog
        self.dlg.show()
        self.dlg.populateCombobox()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            
            #Get the selected Layer and validate
            layerIndex=self.dlg.cbLayers.currentIndex()
            selectedLayer=self.dlg.cbLayers.itemData(layerIndex)
            
            #Validating Layer selected (or not selected)
            if selectedLayer == None or selectedLayer.type()!=QgsMapLayer.VectorLayer:
                QMessageBox.information(self.iface.mainWindow(),"Error","Layer not valid")
                return
            
            #Validating data from text
            try:
                minAngle=float(self.dlg.textAngle.text())
                if minAngle <0 or minAngle >=34:
                    QMessageBox.information(self.iface.mainWindow(),"Error","Angle not valid : Range not valid")
                    return
            except ValueError:
                if(self.dlg.textAngle.text()==""):
                    minAngle=None
                else:
                    QMessageBox.information(self.iface.mainWindow(),"Error","Angle not valid : Not a number")
                    return        
            try:
                maxArea=float(self.dlg.textArea.text())
                if maxArea<=0:
                    QMessageBox.information(self.iface.mainWindow(),"Error","Area not valid : Range not valid")
                    return
            except ValueError:
                if(self.dlg.textArea.text()==""):
                    maxArea=None
                else:
                    QMessageBox.information(self.iface.mainWindow(),"Error","Area not valid : Not a number")
                    return
            try:
                thresholdShapeDescriptor=float(self.dlg.textThresholdDescriptor.text())
                if thresholdShapeDescriptor <0 or thresholdShapeDescriptor> 1:
                   QMessageBox.information(self.iface.mainWindow(),"Error","Threshold not valid : Range not valid")
                   return
            except ValueError:
                QMessageBox.information(self.iface.mainWindow(),"Error","Threshold not valid : Not a number")
                return
                      
            meshName=self.dlg.textName.text()
            if meshName=="":
                meshName="Mesh"
            
            #Obtaining Shape Descriptor Function
            #shapeDescriptor is a function that takes 1 argument (the points) and return the corresponding boolean
            #The threshold is included in the function
            shapeDescriptorIndex=self.dlg.cbShapeDescriptor.currentIndex()
            shapeDescriptor=lambda p: self.dlg.cbShapeDescriptor.itemData(shapeDescriptorIndex)(p,thresholdShapeDescriptor)
            
            #Creating new Vector Layer to return (copying original CRS)
            originalCrs=selectedLayer.crs().toWkt()
            newVectorLayer=QgsVectorLayer("Polygon?crs="+originalCrs,meshName,"memory")
            dataProvider=newVectorLayer.dataProvider()
                        
            newFeaturesToAdd=[]
            
            #Iterating every feature in the selected Layer
            for feature in selectedLayer.getFeatures():
                geometry=feature.geometry()
                points=geometry.asPolygon()
                
                #Validating geometry. We try not dealing with multipart polygons
                if len(points) < 1:
                    print "Invalid Feature ID : "+str(feature.id())
                    continue
                
                #Calculating shape descriptors and restricting what features we don't want to triangulate.
                if len(points)==1 and not shapeDescriptor(points):
                    newFeaturesToAdd.append(feature)
                    continue
                
                newFeatures=[]
                
                #defining things to triangulate
                exteriorBoundary=points.pop(0)
                interiorBoundary=points
                
                #Indicating exterior boundary to triangulate
                trianglePoints=exteriorBoundary
                triangleFacets=simpleFacets(exteriorBoundary)
                triangleHoles=[]
                
                #Indicating interior boundaries to be taken in count when triangulating
                cnt=len(trianglePoints)
                for boundary in interiorBoundary:
                    trianglePoints.extend(boundary)
                    triangleFacets.extend(simpleFacets(boundary,startingCnt=cnt))
                    triangleHoles.extend([getInsidePoint(boundary)])                    
                    cnt+=len(boundary)
                
                #triangulating
                polygon=triangle.MeshInfo()
                polygon.set_points(trianglePoints)
                polygon.set_facets(triangleFacets)
                polygon.set_holes(triangleHoles)
                
                mesh=triangle.build(polygon, min_angle=minAngle,max_volume=maxArea)
                
                #Getting what we need from the result of triangulation
                mesh_points=np.array(mesh.points)
                mesh_triangles=np.array(mesh.elements)
                
                #Adding every triangle as a feature to the new mesh 
                for index in range(0,len(mesh_triangles)):
                    currentIndex=mesh_triangles[index]
                    point1=QgsPoint(mesh_points[currentIndex[0]][0],mesh_points[currentIndex[0]][1])
                    point2=QgsPoint(mesh_points[currentIndex[1]][0],mesh_points[currentIndex[1]][1])
                    point3=QgsPoint(mesh_points[currentIndex[2]][0],mesh_points[currentIndex[2]][1])
                    currentCoords=[point1,point2,point3]
                    newFeature=QgsFeature()
                    newFeature.setGeometry(QgsGeometry.fromPolygon([currentCoords]))
                    newFeatures.append(newFeature)
                
                newFeaturesToAdd.extend(newFeatures)
                    
            dataProvider.addFeatures(newFeaturesToAdd)
            
            #Updating extents
            #newVectorLayer.updateExtents()
            #Temporal solution: copy original extents
            newVectorLayer.setExtent(selectedLayer.extent())
            
            #Make visible the new Layer
            QgsMapLayerRegistry.instance().addMapLayer(newVectorLayer)
            
            
                      
                      
def simpleFacets(points, startingCnt=0):
    #Auxiliar function to return the facets of the polygon. Asuming the order of the points won't change
    #startingCnt defines the number of the initial index.
    #Should be changed?
    ret=[]
    for i in range(0,len(points)-1):
        ret.append([startingCnt+i,startingCnt+i+1])
    ret.append([startingCnt+len(points)-1,startingCnt])
    return ret

def getInsidePoint(points):
    #Auxiliar function to return a point that lies inside of the polygon defined by 'points'
    #Maybe it needs a better algorithm
    #Idea 1 (Bad) : Return the center of the polygon . Could lie outside of the polygon and destroy the entire triangulation :(
    #Idea 2 (Implemented) : Get 3 consecutive points of the boundary. Determine whether the center of the triangle formed is inside the polygon. If not, try with the next triplet.
    #                       Could fail in rare occasions. (when we get a point and this lies on the boundary of the polygon and not detected by pnpoly)
    #                       Could be 'fixed' with a weighted average (biased to the middle point. 
    #Idea 3 : Look for an efficient algorithm to get a single 'ear' 

    for i in range(0,len(points)-1):
        path=Path(points)
        p1=points[i]
        p2=points[(i+1)%len(points)]
        p3=points[(i+2)%len(points)]
        testPoint=[(p1[0]+p2[0]+p3[0])/3,(p1[1]+p2[1]+p3[1])/3]
        if(path.contains_point(testPoint)):
            return testPoint
        
    print "Something went wrong... (getInsidePoint)"
    return []