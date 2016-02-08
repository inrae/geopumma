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
drainage_net_v1=raw_input("Please enter the name of the drainage network : ")




#extraer de river_temp_iter aquellos brazos con distancia cero desde inicio y final
wehere_sql_cero="Up_Str =0 AND Do_Str=0"
grass.run_command("v.extract",input=drainage_net_v1,where=wehere_sql_cero,output='river_temp_iter_no_cero',overwrite=True,flags='r')
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

#while a<10:
while a<len(path_list):
    
    list_checked=path_list[0:a]
    list_no_checked=path_list[a:]
    node_check_i=path_list[a]
    print "revisando el nodo " + str(node_check_i)
    if list_checked.count(node_check_i)==0 and a>0:
        print "esta subiendo"
        #identificar polygono de aguas abajo
        cat_down_stream=path_list[a-1]
        where_sql_9="cat="+str(cat_down_stream)
        Up_Str_prev = grass.read_command("v.db.select",map='river_temp_iter_copy',col='Up_Str',flags='c', where=where_sql_9)
        Up_Str_prev2=Up_Str_prev.rsplit()
        Up_Str_prev3=Up_Str_prev2[0]
        print "Up_Str_prev " +str(Up_Str_prev3)
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
        

grass.run_command("g.copy",vect='river_temp_iter_copy,geo_descriptors_vect',overwrite=True)