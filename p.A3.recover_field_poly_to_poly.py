#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.wtri.py
# AUTHOR(S)     : Sanzana P. 2014
#               
# PURPOSE       : To identify and extract wtri from wti and river maps
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

import sys
import os
import grass.script as grass
directory = os.getcwd()
print directory
import os.path
import shutil

#Declaracion de variables

vectors = grass.read_command("g.list", type='vect')
print vectors
input_map=raw_input("Please enter the name of the input map : ")
output_map=raw_input("Please enter the name of the output map  : ")
base_map=raw_input("Please enter the name of the map with fields : ")
columns = grass.read_command("v.info",map=base_map,flags='c',layer='1')
print columns
id_field=raw_input("Please enter the name of field: ")
type_field=raw_input("Please enter the type (double precision or varchar(80) or int : ")
buffer_selected=raw_input("Please insert buffer to ask the new field (0.1 to 1.0): ")
#si buffer es muy peque?o peude tener problemas

copy_rule=input_map+","+output_map
grass.run_command("g.copy", vect=copy_rule, overwrite=True)

#actulizacion de largos de cada wti
add_rule=id_field+" "+type_field
grass.run_command("v.db.addcol", map=output_map,layer=1,columns=add_rule)


#agregar columna para asignar inicio y final de linea
grass.run_command("v.db.addcol",map=output_map,columns='x double, y double')
grass.run_command("v.to.db",map=output_map,type='line',option='start',columns='x,y')

#borrar todas las columnas que no son id_riv

#deleting columns
output_river=base_map+',polyline'
grass.run_command("g.copy",vect=output_river,overwrite=True)
col = grass.read_command("v.info",map='polyline',flags='c',layer='1')
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
        column=col3[2*n+1]
        if column!=id_field:
                type=col3[2*n].lower()
                del_col=col3[2*n+1]
                print "DELETING COLUMN : " + del_col
                grass.run_command("v.db.dropcol",map='polyline',column=del_col)
                n+=1
        else:
                n+=1

polygons_count = grass.read_command("v.db.select",map=output_map,col='cat',flags='c')
#opcional borrar las cateogrias de los segmentos WTRI que pertencen a SIMBA
#ojo que despues se deben llenar manualmente
c=0

simba_list=['93','813','291','418','292','419','294','421','420','293','595','596']


for i in polygons_count.splitlines():
        if int(i) == 93 or int(i)==813 or int(i)==291 or int(i)==418 or int(i)==292 or int(i)==419 or int(i)==294 or int(i)==421 or int(i)==420 or int(i)==293 or int(i)==595 or int(i)==596:
                print "ELEMENTO SIMBA"
                print "ELEMENTO SIMBA"
                print "ELEMENTO SIMBA"
                print "ELEMENTO SIMBA"
                print "ELEMENTO SIMBA"
                print "ELEMENTO SIMBA"
                print "ELEMENTO SIMBA"
        else:
                #Rellena el campo id river
                print "WORKING ON POLYGON CAT = " + str(i)
                where_sql= "cat=" + str(i)
                grass.run_command("v.extract",input=output_map,output='out_poly_1',where=where_sql,overwrite=True)
                E=grass.read_command("v.db.select",map='out_poly_1',col='x',flags='c',where="cat=%s"%i)
                E1=E.rsplit()
                E2=E1[0]
                N=grass.read_command("v.db.select",map='out_poly_1',col='y',flags='c',where="cat=%s"%i)
                N1=N.rsplit()
                N2=N1[0]
                starting=E2+","+N2
                print starting
                id_riv= grass.read_command("v.what", map='polyline', east_north=starting, flags='a',distance=buffer_selected)
                id_riv1=id_riv.rsplit()
                print id_riv1
                index=id_riv1.index(id_field)+2
                print "id_riv1 = "+str(index)
                id_riv2=id_riv1[index]
                print "Category Id = " +str(i) + " . "+ id_field + " = " + str(id_riv2)
                grass.run_command("v.db.update",map=output_map,column=id_field,value=id_riv2,where="cat=%s"%i)

grass.run_command("v.out.ogr", input=output_map, layer=1, dsn=output_map, overwrite=True)




