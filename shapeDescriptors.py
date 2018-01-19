#Partial implementation of shape descriptors
#Return True if the Shape Descriptor is lesser than the threshold
import numpy as np
import math as m
def funNoShapeDescriptor(points,threshold):
    return True

def funFormFactor(points,threshold):
    area=calcArea(points)
    perimeter=calcPerimeter(points)
    formFactor=4*np.pi*area/perimeter/perimeter
    return formFactor<threshold

def funCompact(points,threshold):
    area=calcArea(points)
    perimeter=calcPerimeter(points)
    compact=m.sqrt(4*np.pi*area)/perimeter
    return compact<threshold

def funSolidityIndex(points,threshold):
    area=calcArea(points)
    convexArea=calcArea(calcConvexHull(points))
    solidityIndex=area/convexArea
    return solidityIndex<threshold

def funConvexityIndex(points,threshold):
    perimeter=calcPerimeter(points)
    convexPerimeter=calcPerimeter(calcConvexHull(points))
    convexityIndex=convexPerimeter/perimeter
    return convexityIndex<threshold


#Auxiliar Functions

def calcArea(points):
    points=points[0]
    area=0.
    ox,oy=points[0]
    for x,y in points[1:]:
        area+=(x*oy-y*ox)
        ox,oy=x,y
    return abs(area/2)

def calcPerimeter(points):
    points=points[0]
    perimeter=0.
    ox,oy=points[0]
    for x,y in points[1:]:
        perimeter+=abs((x-ox)+(y-oy)*1j)
        ox,oy=x,y
    return perimeter

def calcConvexHull(points):
    from scipy.spatial import ConvexHull
    points=np.array(points[0])
    hull=ConvexHull(points)
    realVertices=hull.vertices.tolist()
    realVertices.append(hull.vertices[0])
    convexHullPoints=points[realVertices]
    return [convexHullPoints.tolist()]