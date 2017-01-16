#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.geo_descriptors.py
# AUTHOR(S)     : Sanzana P. 2014
#               
# PURPOSE       : To get database for input of width and area function
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
limit_to_chech_snap=raw_input("Please enter the iterative threshold to check the olaf snapping to river (first try with 1.0 m) : ")
Update_travel_time=raw_input("Please select option to route travel time (Yes=1;No=0) : ")
if Update_travel_time=='1':
        channel_velocity=raw_input("Please enter the velocity in channel (vel aprox = 1.85 m/s) : ")
        hillslope_velocity=raw_input("Please enter the velocity in natural hillslopes areas (vel aprox = 0.05 m/s) : ")
        urban_areas_velocity=raw_input("Please enter the velocity in urban areas (vel aprox = 0.27 m/s) : ")
river_path_add=raw_input("Please select option to use river_path manually modified (Yes=1;No=0) : ")

if river_path_add=='0':

        ####### SEGMENTAR RIO EN AQUELLOS TRAMOS QUE INGRESA OLAF TIPO "RIV"
        #extraer nodos de  malla de interfaces
        grass.run_command("v.to.points",input=olaf_v1,output='nodes', flags='n',overwrite=True)
        #generar buffer al rededor del rio para seleccionar los nodos que segmentaran el rio
        grass.run_command("v.buffer",input=river,output='buffer_out_river',distance='0.01', flags='t',overwrite=True)
        #seleccionar los nodos que estan cerca del buffer
        grass.run_command("v.select",ainput='nodes',binput='buffer_out_river',output='nodes_inside',operator='intersects',overwrite=True)
        grass.run_command("v.select",ainput='nodes',binput='buffer_out_river',output='nodes_outside',operator='disjoint',overwrite=True,flags='r')
        #Check the olaf conections must be maually snnaped
        name_buffer_out_river='buffer_out_river_'+str(int(float(limit_to_chech_snap)*100))+'_cm'
        grass.run_command("v.buffer",input=river,output=name_buffer_out_river,distance=limit_to_chech_snap, flags='t',overwrite=True)
        name_nodes_out_river='nodes_outside_'+str(int(float(limit_to_chech_snap)*100))+'_cm'
        grass.run_command("v.select",ainput='nodes_outside',binput=name_buffer_out_river,output=name_nodes_out_river,operator='intersects',overwrite=True)
        aux_count = grass.read_command("v.db.select",map=name_nodes_out_river,col='cat',flags='c')
        
        if len(aux_count)>0:
                print "##############################################################################"
                print "# WARNING: The nodes of the shape file nodes_outside must be manually snaped #"
                print "# Please edit the olaf nodes and snap manually to river                      #"
                print "# Be careful do not create  boucles                                          #"
                print "# Be careful do not create  boucles                                          #"
                print "##############################################################################"
                #exportar e importar para lim00000pieza topologica topologia
                grass.run_command("v.out.ogr",input=name_nodes_out_river,type='point',dsn=name_nodes_out_river,flags='e',overwrite=True)
                sys.exit()

        #disolver los rios
        grass.run_command("v.build.polylines",input=river,output='river_build',cat='first',overwrite=True)

        #insertar nodos al rio y segmentar todos los tramos
        grass.run_command("v.net",input='river_build',points='nodes_inside',output='estero_segmented',operation='connect',thresh='0.01',overwrite=True,flags='c')
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
        grass.run_command("v.clean",input='river_path',type='line',output='river_path_clean',tool='snap,rmdangle,prune,rmline,rmsa',thresh='0.01',overwrite=True)

        ############ OBTENER DISTANCIA PARA CADA PUNTO DEL RIO A DESEMBOCADURA Y PARA CADA OLAF ADYACENTE AL RIO

        outlet_count = grass.read_command("v.db.select",map='river_path',col='cat',flags='c')

        for i in outlet_count.splitlines():
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
                grass.run_command("v.db.update",map='river_path',col='Do_Str',value=d_min,where=where_sql_1)
        
                d_max=max(dist_1,dist_2)        
                grass.run_command("v.db.update",map='river_path',col='Up_Str',value=d_max,where=where_sql_1)
        
                d_min_2=min(dist_1,dist_2)*100000
                d_max_2=max(dist_1,dist_2)*100000 
                where_sql_2="con_type='channel' AND "+"cat="+str(i)
                grass.run_command("v.db.update",map='river_path',col='id_connect',value=d_min_2,where=where_sql_2)
                grass.run_command("v.db.update",map='river_path',col='id_polyg',value=d_max_2,where=where_sql_2)
        
                where_sql_3="con_type='riv' AND "+"cat="+str(i)
                grass.run_command("v.db.update",map='river_path',col='id_connect',value=d_min_2,where=where_sql_3)

        #check if there are some link unnconted

        aux_count_2 = grass.read_command("v.db.select",map='river_path',col='id_polyg',flags='c',where='id_polyg<0')

        if len(aux_count_2)>0:
                print "##############################################################################"
                print "# WARNING: There are some nodes Upstream and Downstream with uncorrect length#"
                print "# Select the vector file river_path and                                      #"
                print "# Please edit manually the values of the columns  'Do_Str'   'Up_Str'        #"
                print "##############################################################################"
                #exportar e importar para limpieza topologica topologia
                grass.run_command("v.out.ogr",input=name_nodes_out_river,type='point',dsn=name_nodes_out_river,flags='e',overwrite=True)
                sys.exit()

        
if river_path_add=='1':       
        
        outlet_count = grass.read_command("v.db.select",map='river_path',col='cat',flags='c',where='id_polyg<0')
        

        for i in outlet_count.splitlines():
                where_sql_1="cat="+str(i)
                
                Up_Str_prev_temp = grass.read_command("v.db.select",map='river_path',col='Up_Str',flags='c', where=where_sql_1)
                Up_Str_prev_temp2=Up_Str_prev_temp.rsplit()
                Up_Str_prev_temp3=Up_Str_prev_temp2[0]                
                dist_1=float(Up_Str_prev_temp3)
                Up_Do_prev_temp = grass.read_command("v.db.select",map='river_path',col='Do_Str',flags='c', where=where_sql_1)
                Up_Do_prev_temp2=Up_Do_prev_temp.rsplit()
                Up_Do_prev_temp3=Up_Do_prev_temp2[0]  
                dist_2=float(Up_Do_prev_temp3)
                d_min=min(dist_1,dist_2)        

        
                d_min_2=min(dist_1,dist_2)*100000
                d_max_2=max(dist_1,dist_2)*100000 
                where_sql_2="con_type='channel' AND "+"cat="+str(i)
                grass.run_command("v.db.update",map='river_path',col='id_connect',value=d_min_2,where=where_sql_2)
                grass.run_command("v.db.update",map='river_path',col='id_polyg',value=d_max_2,where=where_sql_2)
        
                where_sql_3="con_type='riv' AND "+"cat="+str(i)
                grass.run_command("v.db.update",map='river_path',col='id_connect',value=d_min_2,where=where_sql_3)

        #check if there are some link unnconted

        aux_count_2 = grass.read_command("v.db.select",map='river_path',col='id_polyg',flags='c',where='id_polyg<0')

        if len(aux_count_2)>0:
                print "##############################################################################"
                print "# WARNING: Still persist mistakes in the upstream and downstream distances   #"
                print "# WARNING: There are some nodes Upstream and Downstream with uncorrect length#"
                print "# Select the vector file river_path and                                      #"
                print "# Please edit manually the values of the columns  'Do_Str'   'Up_Str'        #"
                print "##############################################################################"
                #exportar e importar para lim00000pieza topologica topologia
                grass.run_command("v.out.ogr",input=name_nodes_out_river,type='point',dsn=name_nodes_out_river,flags='e',overwrite=True)
                sys.exit()



grass.run_command("v.extract",input='river_path',output='river_path_no_null',where="Do_Str=0 AND Up_Str=0",overwrite=True,flags='r')
grass.run_command("g.copy", vect='river_path_no_null,river_path',overwrite=True)
	
#####################################################################
####ACA SE DEBE AGREGAR UN PATH PARA PEGAR EL river_path con OLAF TIPO 'POLY'
######################################################################

#####################################################################
####ACA SE DEBE AGREGAR UN PATH PARA PEGAR EL river_path con OLAF TIPO 'POLY'
######################################################################
#river_path

grass.run_command("v.extract",input=olaf_v1,output='poly_to_poly',where="con_type='poly'",overwrite=True)
grass.run_command("v.db.addcol",map='poly_to_poly',col='Up_Str double')
grass.run_command("v.db.addcol",map='poly_to_poly',col='Do_Str double')
grass.run_command("v.patch", input='river_path,poly_to_poly', output='river_path_2', overwrite=True,flags='e')

 
 
 
 
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






#extraer de river_temp_iter aquellos brazos con distancia cero desde inicio y final
wehere_sql_cero="Up_Str =0 AND Do_Str=0"
grass.run_command("v.extract",input='river_temp_iter',where=wehere_sql_cero,output='river_temp_iter_no_cero',overwrite=True,flags='r')
grass.run_command("g.copy",vect='river_temp_iter_no_cero,river_temp_iter',overwrite=True)


#recorrer rio en sentido horario



count_index = grass.read_command("v.db.select",map='river_temp_iter',col='cat',flags='c')
count_index2=count_index.rsplit()
count=len(count_index2)
print count

#iniciar el rastreo del arbol a partir del nodo = 0 que corresponde a la salida del cauce
node_i=0
path_list=[]
deleted_list=[]
where_sql_0="id_connect="+str(node_i)
cat_i0 = grass.read_command("v.db.select",map='river_temp_iter',col='cat',flags='c', where=where_sql_0)
cat_i2=cat_i0.rsplit()
cat_i3=cat_i2[0]
path_list.append(cat_i3)

cat_max=path_list[0]


while count>1:
    print "################### INICIO DE WHILE #################"
    #preguntar el comienzo de ese tramo
    print "revisando segmento cat =" + str(path_list[len(path_list)-1])
    print "drena hacia nodo aguas abajo = " + str(node_i)
    where_sql_1="id_connect="+str(node_i)+" AND cat = "+ str(path_list[len(path_list)-1])
    start_index = grass.read_command("v.db.select",map='river_temp_iter',col='id_polyg',flags='c', where=where_sql_1)
    start_index2=start_index.rsplit()
    start_index3=start_index2[0]
    print "drena desde nodo aguas arriba = "  +str(start_index3)
    #preguntar los segmentos vecinos aportantes
    where_sql_2="id_connect="+str(start_index3)
    segm_neig = grass.read_command("v.db.select",map='river_temp_iter',col='cat',flags='c', where=where_sql_2)
    segm_neig2=segm_neig.rsplit()
    print "posee los siguientes vecinos ubicados aguas arriba"
    print segm_neig2
    #Buscar el primer segmento en sentido horario a partir del vector origen
    if len(segm_neig2)>0:
        #iniciar contador de angulos maximos
        delta_ang_list=[360]
        
        #Angulo del primer vector
        x1_coord = grass.read_command("v.db.select",map='river_temp_iter',col='start_E',flags='c', where=where_sql_1)
        x1_coord2=x1_coord.rsplit()
        x1_coord3=x1_coord2[0]
        x1_node_i = float(x1_coord3)
            
        y1_coord = grass.read_command("v.db.select",map='river_temp_iter',col='start_N',flags='c', where=where_sql_1)
        y1_coord2=y1_coord.rsplit()
        y1_coord3=y1_coord2[0]
        y1_node_i = float(y1_coord3)            

        x2_coord = grass.read_command("v.db.select",map='river_temp_iter',col='end_E',flags='c', where=where_sql_1)
        x2_coord2=x2_coord.rsplit()
        x2_coord3=x2_coord2[0]
        x2 = float(x2_coord3)

        y2_coord = grass.read_command("v.db.select",map='river_temp_iter',col='end_N',flags='c', where=where_sql_1)
        y2_coord2=y2_coord.rsplit()
        y2_coord3=y2_coord2[0]
        y2 = float(y2_coord3)


        x = x2 - x1_node_i
        y = y2 - y1_node_i
        angle_vect_1 = math.atan2(y, x) * (180.0 / math.pi)
                
        if angle_vect_1<0:
            angle_vect_1 = angle_vect_1 +360
            
        #print"Angulo en grados del primer vector: " + str(angle_vect_1)


        #Angulo de los vecino
        for i in segm_neig2:

            #Angulo del primer vector
            where_sql_3="cat="+str(i)
            x2_coord = grass.read_command("v.db.select",map='river_temp_iter',col='start_E',flags='c', where=where_sql_3)
            x2_coord2=x2_coord.rsplit()
            x2_coord3=x2_coord2[0]
            x2 = float(x2_coord3)
                
            y2_coord = grass.read_command("v.db.select",map='river_temp_iter',col='start_N',flags='c', where=where_sql_3)
            y2_coord2=y2_coord.rsplit()
            y2_coord3=y2_coord2[0]
            y2 = float(y2_coord3)


            x = x2 - x1_node_i
            y = y2 - y1_node_i
            angle_vect_i = math.atan2(y, x) * (180.0 / math.pi)
                
            if angle_vect_i<0:
                angle_vect_i = angle_vect_i +360
            if angle_vect_i>angle_vect_1:
                delta_ang=(360-angle_vect_i)+angle_vect_1
            if angle_vect_i<angle_vect_1:
                delta_ang=angle_vect_1-angle_vect_i
            if angle_vect_i==angle_vect_1:
                delta_ang=0
                
            print"Angulo entre segmentos "+str(path_list[len(path_list)-1])+"-"+str(i)+" : " + str(delta_ang)
                
            if delta_ang<min(delta_ang_list):
                cat_max=i
                delta_ang_list.append(delta_ang)
    else:
        #Angulo del primer vector
        print "no tengo vecinos, por lo que vuelve a segmento"
        if deleted_list.count(path_list[len(path_list)-2])==0:
            cat_max=path_list[len(path_list)-2]
            print cat_max
            where_sql_5="cat="+str(path_list[len(path_list)-1])
            grass.run_command("v.extract",input='river_temp_iter',where=where_sql_5,output='river_temp_iter_2',overwrite=True,flags='r')
            grass.run_command("g.copy",vect='river_temp_iter_2,river_temp_iter',overwrite=True)
            #agregar segmento borrado a lista
            deleted_list.append(path_list[len(path_list)-1])
            print "elementos borrados son:"
            print deleted_list
        else:
            where_sql_6="id_polyg="+str(node_i)
            cat_max0 = grass.read_command("v.db.select",map='river_temp_iter',col='cat',flags='c', where=where_sql_6)
            cat_max2=cat_max0.rsplit()
            
            #si hay vecinos que no estan conectados una vez que se termina el rastreo aca da error
            #es por ello que se usa como regla de finalizacion
            #se evita esto con la correcta digilitazacion y cambiando snap
            if len(cat_max2)==0:
                count=0
                print "entre aca y el valor de count = " + str(count)
                break
            
            #contador en cero
            
            cat_max3=cat_max2[0]
            cat_max=float(cat_max3)
                
            print "CATEGORIA CONSULTADA DESDE EL Q SE UBICA MAS AGUAS ARRIBA"
            print cat_max
            print "SE BORRARA EL SIGUIENTE ELEMENTO"
            
            where_sql_7="cat="+str(path_list[len(path_list)-1])
            print where_sql_7
            grass.run_command("v.extract",input='river_temp_iter',where=where_sql_7,output='river_temp_iter_2',overwrite=True,flags='r')
            grass.run_command("g.copy",vect='river_temp_iter_2,river_temp_iter',overwrite=True)
            #agregar segmento borrado a lista
            deleted_list.append(path_list[len(path_list)-1])
            print "elementos borrados son:"
            print deleted_list

        
        
    print "vector ubicado mas a la izquierda = "+str(cat_max)
    #agregar vector a la lista de vectores recorridos
    path_list.append(cat_max)
    print "actualizacion de path list"
    print path_list
    #obtener valor del nodo siguiente
    where_sql_4="cat="+str(cat_max)
    next_node_i = grass.read_command("v.db.select",map='river_temp_iter',col='id_connect',flags='c', where=where_sql_4)
    next_node_i2=next_node_i.rsplit()
    next_node_i3=next_node_i2[0]
    node_i = float(next_node_i3)
    print "siguiente nodo (node_i) = "+str(node_i)
    #verificar que todavia quedan tramos por revisar
    #se cuenta la cantidad de tramos que quedan
    count_index = grass.read_command("v.db.select",map='river_temp_iter',col='cat',flags='c')
    count_index2=count_index.rsplit()
    count=len(count_index2)


        
###Actualizar largos
grass.run_command("v.db.addcol",map='river_temp_iter_copy',col='length double')
grass.run_command("v.to.db",map='river_temp_iter_copy',option='length',columns='length')




### Actulizar base de datos

path_list = map(int, path_list)
print path_list

initial_node=int(path_list[0])
flow_direction=-1
a=0


#si se actualiza tabla de velocidades se debe agregar columna 
if Update_travel_time=='1':
        grass.run_command("v.db.addcol",map='river_temp_iter_copy',col='t_Up_Str double')
        grass.run_command("v.db.addcol",map='river_temp_iter_copy',col='t_Do_Str double')
        grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Up_Str',value=0)
        grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Do_Str',value=0)
        #selecting of driver
        grass.run_command("db.connect",driver='sqlite', database='$GISDBASE/$LOCATION_NAME/$MAPSET/sqlite.db')
        grass.run_command("db.connect",flags='p')
        grass.run_command("db.tables",flags='p')
        
        #crear una copia del poligono con los bordes
        copy_1=model_mesh_v1+",model_mesh_v1_2"
        grass.run_command("g.copy", vect=copy_1,overwrite=True)
        copy_2="river_temp_iter_copy,river_temp_iter_copy_sqlite"
        grass.run_command("g.copy", vect=copy_2,overwrite=True)
        
        
        #borrar columna cat_ en caso que exista
        grass.run_command("v.db.dropcol", map='model_mesh_v1_2',column='cat_')
        grass.run_command("v.db.dropcol", map='model_mesh_v1_2',column='area')
        
        
        #The location
        folder_module=directory+"/table_2"
        if os.path.exists(folder_module): 
            shutil.rmtree(folder_module)
            
            print "se borro"
        
        
        grass.run_command("db.out.ogr",input='model_mesh_v1_2', dsn='table_2', format='CSV')
        
        
        dir_module=directory+"/table_2/table_2.csv"
        
        grass.run_command("db.in.ogr",dsn=dir_module)
        grass.run_command("db.dropcol",table='table_2_csv',column='cat',flags='f')
        
        
        #linking with area and slope
        #join
        grass.run_command("v.db.join", map='river_temp_iter_copy_sqlite',column='id_polyg', otable='table_2_csv',ocolumn='id_mesh')
        grass.run_command("db.droptable",flags='f',table='table_2_csv')
        
        #deleting columns
        
        col = grass.read_command("v.info",map='river_temp_iter_copy_sqlite',flags='c',layer='1')
        col1=col.replace("|", " ")
        col2a=col1.replace("PRECISION", " ")
        col2=col2a.replace("CHARACTER", "varchar(80)")
        col3=col2.rsplit()
        print col3
        n=1
        while n < len(col3)/2:
                column=col3[2*n+1]
                if column!="cat" and column!="id" and column!="id_polyg" and column!="id_connect" and column!="con_type" and column!="Up_Str"  and column!="Do_Str"  and column!="area"  and column!="count" and column!="a_1" and column!="a_prev" and column!="a_tot" and column!="length" and column!="module" and column!="t_Up_Str"  and column!="t_Do_Str":
                        type=col3[2*n].lower()
                        del_col=col3[2*n+1]
                        print "DELETING COLUMN : " + del_col
                        grass.run_command("v.db.dropcol",map='river_temp_iter_copy_sqlite',column=del_col)
                        n+=1
                else:
                        n+=1
        
        #volver a driver DBF
        grass.run_command("db.connect",driver='dbf', database='$GISDBASE/$LOCATION_NAME/$MAPSET/dbf/')
        copy_3="river_temp_iter_copy_sqlite,river_temp_iter_copy"
        grass.run_command("g.copy", vect=copy_3,overwrite=True)




#while a<10:
while a<len(path_list):
    
    list_checked=path_list[0:a]
    list_no_checked=path_list[a:]
    node_check_i=path_list[a]
    print "revisando el nodo " + str(node_check_i)
    if list_checked.count(node_check_i)==0 and a>0:
        #update length
        print "esta subiendo"
        #identificar polygono de aguas abajo
        cat_down_stream=path_list[a-1]
        where_sql_9="cat="+str(cat_down_stream)
        Up_Str_prev = grass.read_command("v.db.select",map='river_temp_iter_copy',col='Up_Str',flags='c', where=where_sql_9)
        Up_Str_prev2=Up_Str_prev.rsplit()
        Up_Str_prev3=Up_Str_prev2[0]
        print "length of Up_Str_prev " +str(Up_Str_prev3)
        #identificar polygono actual
        where_sql_10="cat="+str(node_check_i)
        len_i = grass.read_command("v.db.select",map='river_temp_iter_copy',col='length',flags='c', where=where_sql_10)
        len_i2=len_i.rsplit()
        len_i3=len_i2[0]
        print "length_node_i "+str(len_i3)
        len_update=float(Up_Str_prev3)+float(len_i3)
        print "len update "+ str(len_update)
        grass.run_command("v.db.update",map='river_temp_iter_copy',column='Up_Str',value=len_update, where=where_sql_10)
        grass.run_command("v.db.update",map='river_temp_iter_copy',column='Do_Str',value=Up_Str_prev3, where=where_sql_10)
        
    else:
        print "este debe acumular " +str(node_check_i)
        #identificar polygono de aguas arriba
        cat_up_stream=path_list[a-1]
        where_sql_7="cat="+str(cat_up_stream)
        area_prev = grass.read_command("v.db.select",map='river_temp_iter_copy',col='a_1',flags='c', where=where_sql_7)
        area_prev2=area_prev.rsplit()
        area_prev3=area_prev2[0]
        print "area previa " +str(area_prev3)
        #identificar polygono actual
        where_sql_8="cat="+str(node_check_i)
        area_node_i = grass.read_command("v.db.select",map='river_temp_iter_copy',col='a_1',flags='c', where=where_sql_8)
        area_node_i2=area_node_i.rsplit()
        area_node_i3=area_node_i2[0]
        print "area_node_i "+str(area_node_i3)
        area_update=float(area_prev3)+float(area_node_i3)
        print "area update "+ str(area_update)
        grass.run_command("v.db.update",map='river_temp_iter_copy',column='a_1',value=area_update, where=where_sql_8)
        
    a+=1







        #en caso de actualizar columnas con valores de tiempo de viaje
if Update_travel_time=='1':
        where_channel="module IS NULL"
        grass.run_command("v.db.update",map='river_temp_iter_copy',column='module',value="CHANNEL", where=where_channel)
        print "update travel time"
        path_list = map(int, path_list)
        print path_list

        initial_node=int(path_list[0])
        flow_direction=-1
        a=0
        while a<len(path_list):
                list_checked_2=path_list[0:a]
                list_no_checked_2=path_list[a:]
                node_check_i=path_list[a]
                print "revisando el nodo " + str(node_check_i)
                if list_checked_2.count(node_check_i)==0 and a>=0:
                        print "esta subiendo"
                        #identificar polygono de aguas abajo
                        cat_down_stream=path_list[a-1]
                        where_sql_9="cat="+str(cat_down_stream)
                        #identificar el tiempo upstream del polygono de aguas abajo
                        t_Up_Str_prev = grass.read_command("v.db.select",map='river_temp_iter_copy',col='t_Up_Str',flags='c', where=where_sql_9)
                        t_Up_Str_prev2=t_Up_Str_prev.rsplit()
                        t_Up_Str_prev3=t_Up_Str_prev2[0]
                        print "t_Up_Str_prev " +str(t_Up_Str_prev3)
                        
                        #identificar polygono actual
                        where_sql_10="cat="+str(node_check_i)
                        #identificar polygono actual
                        len_i_up = grass.read_command("v.db.select",map='river_temp_iter_copy',col='Up_Str',flags='c', where=where_sql_10)
                        len_i_up2=len_i_up.rsplit()
                        len_i_up3=len_i_up2[0]
                        len_i_do = grass.read_command("v.db.select",map='river_temp_iter_copy',col='Do_Str',flags='c', where=where_sql_10)
                        len_i_do2=len_i_do.rsplit()
                        len_i_do3=len_i_do2[0]
                        len_from_up_to_do=float(len_i_up2[0])-float(len_i_do2[0])
                        print "length_node_i "+str(len_from_up_to_do)
                        #consultar tipo de conexion
                        conexion = grass.read_command("v.db.select",map='river_temp_iter_copy',col='module',flags='c', where=where_sql_10)
                        conexion2=conexion.rsplit()
                        conexion3=conexion2[0]
                        print conexion3
                        print "tipo de conexion es "+str(conexion3)
                        print "la conexion es " + conexion3
                        if conexion3 =="URBS":
                                print "Update urban conexion"
                                time=float(len_from_up_to_do)/float(urban_areas_velocity)
                                time_update=float(t_Up_Str_prev3)+float(time)
                                print "time update "+ str(time_update)
                        if conexion3 =="HEDGE" or conexion3 =="FRER1D":
                                print "Update hillslope conexion"
                                time=float(len_from_up_to_do)/float(hillslope_velocity)
                                time_update=float(t_Up_Str_prev3)+float(time)
                                print "time update "+ str(time_update)
                        if conexion3 =="CHANNEL":
                                print "Update channel conexion"
                                time=float(len_from_up_to_do)/float(channel_velocity)
                                time_update=float(t_Up_Str_prev3)+float(time)
                                print "time update "+ str(time_update)  
                        grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Up_Str',value=time_update, where=where_sql_10)
                        grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Do_Str',value=t_Up_Str_prev3, where=where_sql_10)
                else:
                        print "este debe acumular " +str(node_check_i)
                        #identificar polygono de aguas arriba
                        cat_up_stream=path_list[a-1]
                a+=1









########################################################################################################
#sumar a todos distnacia del primero
##node_correct=path_list[0]
##where_sql_30="cat="+str(node_check_i)
##len_i = grass.read_command("v.db.select",map='river_temp_iter_copy',col='length',flags='c', where=where_sql_30)
##len_i2=len_i.rsplit()
##len_i3=len_i2[0]
##print "length_node_i "+str(len_i3)
###consultar tipo de conexion
##conexion = grass.read_command("v.db.select",map='river_temp_iter_copy',col='module',flags='c', where=where_sql_30)
##print "la conexion es " + conexion
##if conexion =="URBS":
##        time=float(len_i3)/float(urban_areas_velocity)
##if conexion =="HEDGE" or conexion =="FRER1D":
##        time=float(len_i3)/float(hillslope_velocity)
##else:
##        time=float(len_i3)/float(channel_velocity)
##valor_up_str="t_Up_Str +"+str(time)
##valor_do_str="t_Do_Str +"+str(time)
##grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Up_Str',value=valor_up_str)
##grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Do_Str',value=valor_do_str)
##grass.run_command("v.db.update",map='river_temp_iter_copy',column='t_Do_Str',value=0,where=where_sql_30)
#######################################################################################################


grass.run_command("g.copy",vect='river_temp_iter_copy,geo_descriptors_vect',overwrite=True)