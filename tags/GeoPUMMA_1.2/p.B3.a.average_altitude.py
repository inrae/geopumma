#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B3.a.huteur_moyenne.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
# BASED ON  	: hauteur_moyenne.py Paille Y. 01/05/2010
#               
# PURPOSE       : To get statistics from Digital Elevation Model
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
#'''
#Created on mai 2010
#@author: paille
#'''
import grass.script as grass

#'''Affiche le contenu du mapset'''
#'''Display the mapset'''
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
#'''1.- Elegir la capa '''
ogr=raw_input("Please enter the name of the ogr : ")
rasters = grass.read_command("g.list", type='rast')
print rasters
#'''2.- Elegir el DEM '''
dem=raw_input("Please enter the name of the raster : ")
#'''2.- Elegir el DEM '''
rast_prefix=raw_input("Please enter the name of the colprex : ")


#'''2. calcul de la hauteur moyenne'''
#'''2. calculating the average height'''
grass.run_command("v.rast.stats", flags='c', map=ogr, layer='1', raster=dem, column_prefix='dem', overwrite=True) 
grass.run_command("v.db.dropcolumn", map=ogr, layer='1', column='dem_number')
grass.run_command("v.db.dropcolumn", map=ogr, layer='1', column='dem_variance')
grass.run_command("v.db.dropcolumn", map=ogr, layer='1', column='dem_coeff_var')



name1="dem_average,"+rast_prefix+"_ave"
grass.run_command("v.db.renamecolumn", map=ogr, layer='1', column=name1)


#Rellenar altura de aquellos poligonos con 
polygons=ogr
col_fill=rast_prefix+"_ave"
grass.run_command("g.region",rast=dem)
grass.run_command("v.db.addcolumn", map=polygons, columns="E double,N double")
grass.run_command("v.to.db", map=polygons, option='coor', col='E, N')
condition=col_fill+" IS NULL"
grass.run_command("v.extract", input=polygons, output='polygons_temp', where=condition, overwrite=True,flags='r')
list_column_1=grass.read_command("v.db.select",map='polygons_temp',columns='cat',flags='c')
list_column_2=grass.read_command("v.db.select",map=ogr,columns='cat',flags='c')

if len(list_column_1)<len(list_column_2):

	for i in list_column.splitlines():
		coordinates = grass.read_command("v.db.select",map='polygons_temp', where="cat=%s"%i, columns='E,N', flags='c', separator=" ")
		c_1=coordinates.rsplit()
		E=c_1[0]
		N=c_1[1]
		centr=E+","+N
		print "Filling Polygon Cat: "+ str(i)
		print "Coordinates centroid: " + centr
		value=grass.read_command("r.what", input=dem, separator=' ', east_north=centr)
		print value
		v_1=value.rsplit()
		v_3=v_1[2]
		print v_3
		where_sql_1="cat="+str(i)
		grass.run_command("v.db.update",map=polygons,col=col_fill,value=v_3,where=where_sql_1)
		col_value_1=0
		grass.run_command("v.db.update",map=polygons,column='dem_stddev',value=0,where=where_sql_1)
		grass.run_command("v.db.update",map=polygons,column='dem_minimum',value=v_3,where=where_sql_1)
		grass.run_command("v.db.update",map=polygons,column='dem_maximum',value=v_3,where=where_sql_1)
		grass.run_command("v.db.update",map=polygons,column='dem_first_quartile',value=v_3,where="cat=%s"%i)
		grass.run_command("v.db.update",map=polygons,column='dem_third_quartile',value=v_3,where="cat=%s"%i)
grass.run_command("v.db.dropcolumn", map=polygons, column='N')
grass.run_command("v.db.dropcolumn", map=polygons, column='E')
grass.run_command("v.db.dropcolumn", map=polygons, column='dem_first_quartile')
grass.run_command("v.db.dropcolumn", map=polygons, column='dem_median')
grass.run_command("v.db.dropcolumn", map=polygons, column='dem_third_quartile')
grass.run_command("v.db.dropcolumn", map=polygons, column='dem_percentile_90')
grass.run_command("v.db.dropcolumn", map=polygons, column='dem_range')
grass.run_command("v.db.dropcolumn", map=polygons, column='dem_sum')
grass.run_command("g.remove", flags='f', name='polygons_temp',type='vector', overwrite=True)

#cambiar nombre final
name2="dem_stddev,"+rast_prefix+"_std"
grass.run_command("v.db.renamecolumn", map=ogr, layer='1', column=name2)
name3="dem_minimum,"+rast_prefix+"_min"
grass.run_command("v.db.renamecolumn", map=ogr, layer='1', column=name3)
name4="dem_maximum,"+rast_prefix+"_max"
grass.run_command("v.db.renamecolumn", map=ogr, layer='1', column=name4)
#name5="dem_first_quartile,"+rast_prefix+"_1quar"
#grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name5)
#name6="dem_third_quartile,"+rast_prefix+"_3quar"
#grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name6)





