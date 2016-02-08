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



####### SEGMENTAR RIO EN AQUELLOS TRAMOS QUE INGRESA OLAF TIPO "RIV"
#extraer nodos de  malla de interfaces
grass.run_command("v.to.points",input=olaf_v1,output='nodes', flags='n',overwrite=True)
#generar buffer al rededor del rio para seleccionar los nodos que segmentaran el rio
grass.run_command("v.buffer",input=river,output='buffer_out_river',distance='0.010', flags='t',overwrite=True)
#seleccionar los nodos que estan cerca del buffer
grass.run_command("v.select",ainput='nodes',binput='buffer_out_river',output='nodes_inside',operator='intersects',overwrite=True)

#disolver los rios
grass.run_command("v.build.polylines",input=river,output='river_build',cat='first',overwrite=True)

#insertar nodos al rio y segmentar todos los tramos
grass.run_command("v.net",input='river_build',points='nodes_inside',output='estero_segmented',operation='connect',thresh='0.001',overwrite=True,flags='c')
#cambiar nombre de columna cat_, eliminar si es posible en ubuntu, porque grass windows 7 no deja
grass.run_command("v.db.dropcol",map='estero_segmented',column='cat_')

#exportar e importar para limpieza topologica topologia
grass.run_command("v.out.ogr",input='estero_segmented',type='line',dsn='estero_segmented_folder',flags='e',overwrite=True)

#v.in.ogr -o --overwrite dsn=C:\script\wti_deleted_small_length.shp
folder=directory+"/estero_segmented_folder/estero_segmented.shp"
grass.run_command("v.in.ogr",dsn=folder,output='estero_segmented_cat',flags='o',overwrite=True)
grass.run_command("v.db.dropcol",map ='estero_segmented_cat', column='cat_')

#agregar columna con largo para borrar aquellas menores a 0.1
grass.run_command("v.db.addcol",map='estero_segmented_cat',col='length double') 
#calcula el largo
grass.run_command("v.to.db", map='estero_segmented_cat',option='length',columns='length')
#selecciona solo los que tienen un largo mayor a 0.1
grass.run_command("v.extract",input='estero_segmented_cat',output='estero_segmented_cat_length',where="length>0.001",overwrite=True)


#disolver los tramos menos a un limite
grass.run_command("v.clean",input='estero_segmented_cat_length',output='estero_clean',tool='snap',thres=0.001,overwrite=True)
#calcular el nuevo largo despues de disolver
grass.run_command("v.to.db",map='estero_clean',option='length',columns='length')
#selecciona solo los que tienen un largo mayor a 0.001
grass.run_command("v.extract",input='estero_clean',output='estero_segmented_dissolved',where="length>0",overwrite=True)

#exportar e importar para limpieza topologica topologia
output='estero_segmented_dissolved,'+'out_river'
grass.run_command("g.copy",vect=output,overwrite=True)
#agregar columna con largo para borrar aquellas menores a 0.1
grass.run_command("v.db.addcol",map='out_river',col='id int')
grass.run_command("v.db.update", map='out_river',layer=1,column='id', value='cat')


folder_1=directory+"/estero_segmented_folder/"
if os.path.exists(folder_1): 
    shutil.rmtree(folder_1)
    print "Deleting ... " + folder_1
    
grass.run_command("g.remove",vect='buffer_out_river,estero_clean,estero_segmented,estero_segmented_cat,estero_segmented_cat_length,estero_segmented_dissolved,nodes,nodes_inside')

########### UNIR RIO SEGMENTADO CON OLAF TIPO RIV
grass.run_command("v.db.dropcol",map=olaf_v1,column='cat_')
grass.run_command("v.extract",input=olaf_v1,output='poly_to_riv',where="con_type='riv'",overwrite=True)

#borrar todas las columnas que no son id_riv

#deleting columns

grass.run_command("g.copy",vect='out_river,river',overwrite=True)
col = grass.read_command("v.info",map='river',flags='c',layer='1')
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
        column=col3[2*n+1]
        if column!="cat":
                type=col3[2*n].lower()
                del_col=col3[2*n+1]
                print "DELETING COLUMN : " + del_col
                grass.run_command("v.db.dropcol",map='river',column=del_col)
                n+=1
        else:
                n+=1

grass.run_command("v.db.addcol",map='river',column='id int')
grass.run_command("v.db.addcol",map='river',column='id_polyg int')
grass.run_command("v.db.addcol",map='river',column='id_connect int')
grass.run_command("v.db.addcol",map='river',column='con_type varchar(15)')
grass.run_command("v.db.update",map='river',col='con_type',value='channel')

path_rule="poly_to_riv,river"
grass.run_command("v.patch", input=path_rule, output="river_path", overwrite=True,flags='e')
grass.run_command("v.db.addcol",map='river_path',col='Up_Str double')
grass.run_command("v.db.addcol",map='river_path',col='Do_Str double')
grass.run_command("v.clean",input='river_path',type='line',output='river_path_clean_0',tool='snap,break,rmdangle,prune,rmline,rmsa',thresh='0.1',overwrite=True)

#exportar e importar para limpieza topologica
grass.run_command("v.db.dropcol",map='river_path_clean_0',column='cat_')
grass.run_command("v.out.ogr",input="river_path_clean_0",type='line',dsn="river_path_clean_0",flags='e',overwrite=True)


folder=directory+"/river_path_clean_0/river_path_clean_0.shp"
grass.run_command("v.in.ogr",dsn=folder,output='river_path_clean',flags='o',overwrite=True)
grass.run_command("v.db.dropcol",map='river_path_clean',column='cat_')

############ OBTENER DISTANCIA PARA CADA PUNTO DEL RIO A DESEMBOCADURA Y PARA CADA OLAF ADYACENTE AL RIO

outlet_count = grass.read_command("v.db.select",map='river_path_clean',col='cat',flags='c')
for i in outlet_count.splitlines():
#for i in [3067]:
        river_where="cat="+str(i)
        grass.run_command("v.extract",input='river_path_clean',output='river_path_1',where=river_where,overwrite=True)
        grass.run_command("v.to.points",input='river_path_1',output='nodes_riv', flags='n',overwrite=True)
        path_rule="nodes_riv,"+outlet_t
        grass.run_command("v.patch", input=path_rule, output="nodes_tot", overwrite=True)
        grass.run_command("v.out.ogr",input='nodes_tot',type='point',dsn='folder_nodes_riv',flags='e',overwrite=True)
        folder2=directory+"/folder_nodes_riv/nodes_tot.shp"
        grass.run_command("v.in.ogr",dsn=folder2,output='nodes_tot_2',flags='o',overwrite=True)
        grass.run_command("v.net",input="river_path_clean",points='nodes_tot_2',output='river_points',operation='connect',thresh='0.1',overwrite=True)
        dist_1=0
        dist_2=0
        for n in [1,2]:
                c=open("goto.txt","w")
                text="1 " + str(n)+" "+str(3)
                print "texto de nodo a nodo "
                print text
                c.write(text)
                c.close()
                grass.run_command("v.net.path",input='river_points',out='path_temp',file='goto.txt',overwrite=True)
                if n == 1:
                        dist_1_no_round =grass.read_command("v.db.select",map='path_temp',col='cost',flags='c')
                        dist_1 =round(float(dist_1_no_round),3)
                else:
                        dist_2_no_round =grass.read_command("v.db.select",map='path_temp',col='cost',flags='c')
                        dist_2 =round(float(dist_2_no_round),3)
        #Actualizar valores 
        where_sql_1="cat="+str(i)
        d_min=min(dist_1,dist_2)        
        grass.run_command("v.db.update",map='river_path_clean',col='Do_Str',value=d_min,where=where_sql_1)
        
        d_max=max(dist_1,dist_2)        
        grass.run_command("v.db.update",map='river_path_clean',col='Up_Str',value=d_max,where=where_sql_1)
        
        d_min_2=min(dist_1,dist_2)*100000
        d_max_2=max(dist_1,dist_2)*100000
        where_sql_2="con_type='channel' AND "+"cat="+str(i)
        grass.run_command("v.db.update",map='river_path_clean',col='id_connect',value=d_min_2,where=where_sql_2)
        grass.run_command("v.db.update",map='river_path_clean',col='id_polyg',value=d_max_2,where=where_sql_2)
        
        where_sql_3="con_type='riv' AND "+"cat="+str(i)
        grass.run_command("v.db.update",map='river_path_clean',col='id_connect',value=d_min_2,where=where_sql_3)

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
