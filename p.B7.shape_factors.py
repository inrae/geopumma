#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B7.shape_factors.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
#               
# PURPOSE       : To estimate the principal shape factors for polygons:
#                 area, perimeter, compact,convexity,solidity,formfactor
#               
# COPYRIGHT     : IRSTEA-UC-UCH
# This file is part of GeoPUMMA
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
#
#############################################################################
#
#
#
import grass.script as grass
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygon map : ")
#Add new colums
grass.run_command("v.db.addcol",map=polygons,col="AREA double")
grass.run_command("v.db.addcol",map=polygons,col="PERIMETER double")
grass.run_command("v.db.addcol",map=polygons,col="SOLIDITY double")
grass.run_command("v.db.addcol",map=polygons,col="CONVEXITY double")
grass.run_command("v.db.addcol",map=polygons,col="COMPACT double")
grass.run_command("v.db.addcol",map=polygons,col="FORMFACTOR double")
#Calculate Area, Perimeter y Compactness with v.to.db function
grass.run_command("v.to.db", map=polygons,option='area',col='AREA')
grass.run_command("v.to.db", map=polygons,option='perimeter',col='PERIMETER')
grass.run_command("v.to.db", map=polygons,option='compact',col='COMPACT')
polygons_count = grass.read_command("v.db.select",map=polygons,col='cat',flags='c')
grass.run_command("g.region", vect=polygons)
#Calculating solidity, convexity,roundness,formfactor
for i in polygons_count.splitlines():
    print "WORKING ON POLYGON CAT = " + str(i)
    grass.run_command("v.extract",input=polygons,output='out_poly_1',where="cat=%s"%i,overwrite=True)
    area=grass.read_command("v.db.select",map=polygons,col='AREA',flags='c',where="cat=%s"%i)
    area1=area.rsplit()
    area2=area1[0]
    peri=grass.read_command("v.db.select",map=polygons,col='PERIMETER',flags='c',where="cat=%s"%i)
    peri1=peri.rsplit()
    peri2=peri1[0]
    #FORM FACTOR
    import math
    form_fact=4*4*float(area2)/(float(peri2)*float(peri2))
    grass.run_command("v.db.update",map=polygons,col='FORMFACTOR',value=form_fact,where="cat=%s"%i)
    #CONVEX HULL
    grass.run_command("g.region", vect=polygons)
    points = grass.read_command("v.to.points",input='out_poly_1',output='points_temp_0',flags='v',  overwrite=True)
    grass.run_command("v.hull", input='points_temp_0', output='out_poly_hull', overwrite=True, flags='a')
    grass.run_command("v.db.addtable",map='out_poly_hull')
    grass.run_command("v.db.addcol",map='out_poly_hull',col="AREA double")
    grass.run_command("v.db.addcol",map='out_poly_hull',col="PERIMETER double")
    grass.run_command("v.to.db", map='out_poly_hull',option='area',col='AREA')
    grass.run_command("v.to.db", map='out_poly_hull',option='perimeter',col='PERIMETER')
    #Solidity and Convexity
    harea=grass.read_command("v.db.select",map='out_poly_hull',col='AREA',flags='c')
    harea1=harea.rsplit()
    harea2=harea1[0]
    print "harea 2"+harea2
    hperi=grass.read_command("v.db.select",map='out_poly_hull',col='PERIMETER',flags='c')
    hperi1=hperi.rsplit()
    hperi2=hperi1[0]
    print "hperi 2"+hperi2
    soli=float(area2)/float(harea2)
    conv=float(hperi2)/float(peri2)
    print "convexity = " + str(conv)
    print "area "+str(area2)
    print "harea "+str(harea2)
    #checking if it is necessary correct when convexity area is less than polygon area
    if float(harea2)<float(area2):
        points = grass.read_command("v.to.points",input='out_poly_1',output='points_temp_0',flags='vi',dmax='0.1',  overwrite=True)
        grass.run_command("v.hull", input='points_temp_0', output='out_poly_hull', overwrite=True, flags='a')
        grass.run_command("v.db.addtable",map='out_poly_hull')
        grass.run_command("v.db.addcol",map='out_poly_hull',col="AREA double")
        grass.run_command("v.db.addcol",map='out_poly_hull',col="PERIMETER double")
        grass.run_command("v.to.db", map='out_poly_hull',option='area',col='AREA')
        grass.run_command("v.to.db", map='out_poly_hull',option='perimeter',col='PERIMETER')
        #Solidity and Convexity
        harea=grass.read_command("v.db.select",map='out_poly_hull',col='AREA',flags='c')
        harea1=harea.rsplit()
        harea2=harea1[0]
        print "harea 2"+harea2
        hperi=grass.read_command("v.db.select",map='out_poly_hull',col='PERIMETER',flags='c')
        hperi1=hperi.rsplit()
        hperi2=hperi1[0]
        print "hperi 2"+hperi2
        soli=float(area2)/float(harea2)
        conv=float(hperi2)/float(peri2)
        print "convexity = " + str(conv)
    else:
        print conv
    grass.run_command("v.db.update",map=polygons,col='SOLIDITY',value=soli,where="cat=%s"%i)
    grass.run_command("v.db.update",map=polygons,col='CONVEXITY',value=conv,where="cat=%s"%i)
