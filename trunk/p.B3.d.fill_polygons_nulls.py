#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B3.d.fill_polygons_null.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
#               
# PURPOSE       : To fill polygons with null values in the statistic step
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
#Fill null polygons values
import grass.script as grass
#####Display the mapset content#####
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygons : ")
columns=grass.read_command("v.info", map=polygons, flags='c')
print columns
col_fill=raw_input("Please enter the name of the column that you desire to fill: ")
raster = grass.read_command("g.list", type='rast')
print raster
dem=raw_input("Please enter the name of the dem to fill column values : ")
grass.run_command("g.region",rast=dem)
grass.run_command("v.db.addcolumn.py", map=polygons, column="E double,N double")
grass.run_command("v.to.db", map=polygons, option='coor', col='E, N')
condition=col_fill+" IS NULL"
grass.run_command("v.extract", input=polygons, output='polygons_temp', where=condition, overwrite=True)
list_column=grass.read_command("v.db.select",map='polygons_temp',col='cat',flags='c')
for i in list_column.splitlines():
    coordinates = grass.read_command("v.db.select",map='polygons_temp', where="cat=%s"%i, col='E,N', flags='c', separator=" ")
    c_1=coordinates.rsplit()
    E=c_1[0]
    N=c_1[1]
    centr=E+","+N
    print "Filling Polygon Cat: "+ str(i)
    print "Coordinates centroid: " + centr
    value=grass.read_command("r.what", map=dem, separator=' ', coordinates=centr)
    print value
    v_1=value.rsplit()
    v_3=v_1[2]
    print v_3
    grass.run_command("v.db.update",map=polygons,col=col_fill,value=v_3,where="cat=%s"%i)
grass.run_command("v.db.dropcolumn.py", map=polygons, column='N')
grass.run_command("v.db.dropcolumn.py", map=polygons, column='E')
grass.run_command("g.remove", flags='f', vect='polygons_temp', overwrite=True)



