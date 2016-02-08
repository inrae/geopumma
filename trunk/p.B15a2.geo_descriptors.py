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
env = grass.gisenv()
print env
directory = os.getcwd()
print directory
import os.path
import shutil
import math

#Declaracion de variables

vectors = grass.read_command("g.list", type='vect')
print vectors
model_mesh_v1=raw_input("Please enter the name of the model mesh : ")
olaf_v1=raw_input("Please enter the name of the map with olaf path way : ")
river=raw_input("Please enter the name of the river : ")
outlet_t=raw_input("Please enter the name of the out : ")
drainage_network_v1 = raw_input("Please enter the name of the drainage network out : ")



#####################################################################
####ACA SE DEBE AGREGAR UN PATH PARA PEGAR EL river_path con OLAF TIPO 'POLY'
######################################################################
#river_path

grass.run_command("v.extract",input=olaf_v1,output='poly_to_poly',where="con_type='poly'",overwrite=True)
grass.run_command("v.db.addcol",map='poly_to_poly',col='Up_Str double')
grass.run_command("v.db.addcol",map='poly_to_poly',col='Do_Str double')
grass.run_command("v.patch", input='river_path_clean,poly_to_poly', output='river_path_2', overwrite=True,flags='e')

 
#selecting of driver
grass.run_command("db.connect",driver='sqlite', database='$GISDBASE/$LOCATION_NAME/$MAPSET/sqlite.db')
grass.run_command("db.connect",flags='p')
grass.run_command("db.tables",flags='p')

#crear una copia del poligono con los bordes
copy_1=model_mesh_v1+",model_mesh_v1"
grass.run_command("g.copy", vect=copy_1,overwrite=True)
copy_2="river_path_2,river_path_sqlite"
grass.run_command("g.copy", vect=copy_2,overwrite=True)


#borrar columna cat_ en caso que exista
grass.run_command("v.db.dropcol", map='model_mesh_v1',column='cat_')


#The location
folder_module=directory+"/table"
if os.path.exists(folder_module): 
    shutil.rmtree(folder_module)
    
    print "se borro"


grass.run_command("db.out.ogr",input='model_mesh_v1', dsn='table', format='CSV')


dir_module=directory+"/table/table.csv"

grass.run_command("db.in.ogr",dsn=dir_module)
grass.run_command("db.dropcol",table='table_csv',column='cat',flags='f')


#linking with area and slope
grass.run_command("v.db.join", map='river_path_sqlite',column='id_polyg', otable='table_csv',ocolumn='id_mesh')
grass.run_command("db.droptable",flags='f',table='table_csv')

#deleting columns

col = grass.read_command("v.info",map='river_path_sqlite',flags='c',layer='1')
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
        column=col3[2*n+1]
        if column!="cat" and column!="id" and column!="id_polyg" and column!="id_connect" and column!="con_type" and column!="Up_Str"  and column!="Do_Str"  and column!="area"  and column!="alt" and column!="wood_m2" and column!="imp_m2" and column!="mat_m2":
                type=col3[2*n].lower()
                del_col=col3[2*n+1]
                print "DELETING COLUMN : " + del_col
                grass.run_command("v.db.dropcol",map='river_path_sqlite',column=del_col)
                n+=1
        else:
                n+=1
grass.run_command("v.db.update",map='river_path_sqlite',col='area',value=0,where="con_type='channel'")

#volver a driver DBF
grass.run_command("db.connect",driver='dbf', database='$GISDBASE/$LOCATION_NAME/$MAPSET/dbf/')
grass.run_command("db.connect",flags='p')
grass.run_command("db.tables",flags='p')

copy_3="river_path_sqlite,river_path_dbf"
grass.run_command("g.copy", vect=copy_3,overwrite=True)
grass.run_command("v.db.addcol",map='river_path_dbf',column='count int')
grass.run_command("v.db.addcol",map='river_path_dbf',column='a_1 double precision')
grass.run_command("v.db.addcol",map='river_path_dbf',column='a_prev double precision')
grass.run_command("v.db.addcol",map='river_path_dbf',column='a_tot double precision')




#iniciar contador en 0
grass.run_command("v.db.update",map='river_path_dbf',col='count',value=0)
grass.run_command("v.db.update",map='river_path_dbf',col='a_1',value='area')
grass.run_command("v.db.update",map='river_path_dbf',col='a_prev',value=0)
grass.run_command("v.db.update",map='river_path_dbf',col='a_tot',value=0)



#exportar e importar para limpieza topologica
grass.run_command("v.db.dropcol",map='river_path_dbf',column='cat_')
grass.run_command("v.out.ogr",input="river_path_dbf",type='line',dsn="olaf_folder_river",flags='e',overwrite=True)


folder=directory+"/olaf_folder_river/river_path_dbf.shp"
grass.run_command("v.in.ogr",dsn=folder,output='river_temp_iter',flags='o',overwrite=True)


grass.run_command("v.db.dropcol",map='river_temp_iter',column='cat_')
grass.run_command("v.db.update",map='river_temp_iter',column='id',value='cat')
grass.run_command("g.copy",vect='river_temp_iter,river_temp_iter_copy',overwrite=True)


#Agregar coordenadas inicio y termino
grass.run_command("v.db.addcol",map='river_temp_iter',col='start_E double,start_N double,end_E double,end_N double')
grass.run_command("v.to.db",map='river_temp_iter',option='start',columns='start_E,start_N')
grass.run_command("v.to.db",map='river_temp_iter',option='end',columns='end_E,end_N')

#exportar e importar para limpieza topologica
copy_rule='river_temp_iter,'+drainage_network_v1
grass.run_command("g.copy",vect=copy_rule,overwrite=True)
grass.run_command("v.db.dropcol",map=drainage_network_v1,column='cat_')
grass.run_command("v.out.ogr",input=drainage_network_v1,type='line',dsn=drainage_network_v1,flags='e',overwrite=True)


















