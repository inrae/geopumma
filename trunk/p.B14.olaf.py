#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.OLAF.py
# AUTHOR(S)     : Sanzana P. 01/12/2014
# BASED ON  	: interOLAF.py Florent B. 10/01/2011
#               
# PURPOSE       : Identifying OLAF using information of WTI & WTRI
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
import sys
import os
import grass.script as grass
env = grass.gisenv()
print env
directory = os.getcwd()
print directory
import os.path
import shutil

#1.-imprimir vectores disponibles y definir nombre de polygonos
vectors = grass.read_command("g.list", type='vect')
print vectors
model_mesh=raw_input("Please enter the name of the map with polygon mesh : ")
columns = grass.read_command("v.info",map=model_mesh,flags='c',layer='1')
print columns
column_alt=raw_input("Please enter the name of the column with altitude value : ")
wtri_v1=raw_input("Please enter the name of the wtri : ")
wti_v0=raw_input("Please enter the name of the wti : ")
estero_segm=raw_input("Please enter the name of the segmented river : ")
olaf_output_vector=raw_input("Please enter the name of the olaf output vector : ")



#2.-Generar lista con poligonos vecinos al rio
polygons_river=grass.read_command("v.db.select",map=wtri_v1,col='id_mesh',flags='c')
polygons_river2=polygons_river.rsplit()
polygons_river3=sorted(polygons_river2)
#inicializar variables auxiliares
x=0
list_polygons_river3=[]

#Delete repeted values
while x<len(polygons_river3):
    c=int(polygons_river3[x])
    if list_polygons_river3.count(c) ==0:
        list_polygons_river3.append(c) 
    else :
        print "Repeted Value "+ str(c)
    x+=1
list_polygons_river_sorted=sorted(list_polygons_river3)
# prueba de recursividad inicia en 2373 y termina en 2641
#list_polygons_river_sorted.append(2641)
print list_polygons_river_sorted

#agregar columna a model mesh con id river
grass.run_command("v.db.addcol",map=model_mesh,columns='id_temp int')


#Unir poligonos al rio
a=0
for i in list_polygons_river_sorted:
#for i in [303,304]:
    cat1="poly_"+str(i)
    where_sql='id_mesh='+str(i)
    grass.run_command("v.extract",input=model_mesh,where=where_sql,output=cat1,overwrite=True)
    distance_i="dist_"+str(i)
    grass.run_command("v.distance",_from=cat1,to=estero_segm,out='dist_temp',from_type='centroid', to_type='line',upload='to_attr',to_column='id',column='id_temp',overwrite=True)
    grass.run_command("v.db.addtable",map='dist_temp', columns='id int,id_polyg int,id_connect int,con_type varchar(15)')
    grass.run_command("v.category",input='dist_temp',output=distance_i,option='add',overwrite=True)
    grass.run_command("v.to.db", map=distance_i,option='cat')
    grass.run_command("v.db.update",map=distance_i,column='id_polyg',value=i)
    grass.run_command("v.db.update",map=distance_i,column='con_type',value="riv")
    id_reach=grass.read_command("v.db.select",map=cat1,column='id_temp',flags='c')
    grass.run_command("v.db.update",map=distance_i,column='id_connect',value=id_reach)
    if a==0:
	copy=distance_i+",poly_to_river_temp_1"
	grass.run_command("g.copy",vect=copy,overwrite=True)
	grass.run_command("g.remove",vect=distance_i)
	grass.run_command("g.remove",vect=cat1)
	a+=1
    else:
	patch="poly_to_river_temp_1,"+distance_i
	grass.run_command("v.patch", input=patch, output='poly_to_river_temp_2', overwrite=True,flags='e')
	grass.run_command("g.copy",vect='poly_to_river_temp_2,poly_to_river_temp_1', overwrite=True)
	grass.run_command("g.remove",vect=distance_i)
	grass.run_command("g.remove",vect=cat1)
	a+=1





#Buscar vecinos para cada subcuenca

subb_count = grass.read_command("v.db.select",map=model_mesh,col='id_subb_2',flags='c')
#Delete repeted values
subb_count2=subb_count.rsplit()
subb_count3=sorted(subb_count2)
#inicializar variables auxiliares
x=0
subb_count_4=[]
while x<len(subb_count3):
    c=int(subb_count3[x])
    if subb_count_4.count(c) ==0:
        subb_count_4.append(c) 
    else :
        print "Repeted Value "+ str(c)
    x+=1
subb_count_sorted=sorted(subb_count_4)

#Definir lista de subcuencas que poseen falsas depresiones
subb_with_false_depresion = []


for s in subb_count_sorted:
#for s in [12]:
    #colocar valor -1 a todos los poligonos vecinos que no corresponden a la subcuenca "s"
    where_sql_sbb="subb_a='"+str(s)+"' OR subb_b='"+str(s)+"'"
    grass.run_command("v.extract",input=wti_v0,output='wti_sbb_temp',where=where_sql_sbb,overwrite=True)
    where_update_a="NOT subb_a='"+str(s)+"'"
    grass.run_command("v.db.update",map='wti_sbb_temp',column='id_mesh_a',value=-1,where=where_update_a)
    where_update_b="NOT subb_b='"+str(s)+"'"
    grass.run_command("v.db.update",map='wti_sbb_temp',column='id_mesh_b',value=-1,where=where_update_b)
    #renombrar variable
    wti_v1='wti_sbb_temp'
    
    
    subb_query='id_subb_2='+str(s)
    polygons_count = grass.read_command("v.db.select",map=model_mesh,col='id_mesh',flags='c', where=subb_query)
    polygons_count2=polygons_count.rsplit()
    polygons_count3=sorted(polygons_count2)
    
        
    #conservar solo valores que no estan cercanos al rio
    x=0
    cat_no_river=[]
    false_depresion_list=[]
    
    
    while x<len(polygons_count3):
	c=int(polygons_count3[x])
	if list_polygons_river_sorted.count(c) ==0:
	    cat_no_river.append(c) 
	else :
	    print "Repeted Value "+ str(c)
	x+=1
    cat_no_river_sorted=sorted(cat_no_river)
    
    #seleccionar poligonos que solo tienen un vecino
    isolated_list=[]
    for q in cat_no_river_sorted:
	#listar vecinos de columna left id_mesh_a
	condition_id_mesh_b = "id_mesh_b="+str(q)
	neig_a =grass.read_command("v.db.select",map=wti_v1,col='id_mesh_a',flags='c',where=condition_id_mesh_b)
	neig_a2=neig_a.rsplit()
	neig_a3=sorted(neig_a2)
	a=0
	b=0
	c=0
	list=[]
	#Delete repeted values
	print neig_a3
	while b<len(neig_a3):
	    c=int(neig_a3[b])
	    if list.count(c) ==0:
		list.append(c)
		print "Added "+ str(c)
	    else :
		print "Repeted Value "+ str(c)
	    b+=1
	sorted_neig=sorted(list)
	print sorted_neig
	    
	#listar vecinos de columna rigth id_mesh_b
	condition_id_mesh_a = "id_mesh_a="+str(q)
	neig_b =grass.read_command("v.db.select",map=wti_v1,col='id_mesh_b',flags='c',where=condition_id_mesh_a)
	neig_b2=neig_b.rsplit()
	neig_b3=sorted(neig_b2)
	a=0
	b=0
	c=0
	#Delete repeted values
	print neig_b3
	while b<len(neig_b3):
	    c=int(neig_b3[b])
	    if sorted_neig.count(c) ==0:
		sorted_neig.append(c)
		print "Added "+ str(c)
	    else :
		print "Repeted Value "+ str(c)
	    b+=1
	sorted_neig_b=sorted(sorted_neig)
	print sorted_neig_b
	
	if len(sorted_neig_b)==2 and sorted_neig_b.count(-1)>0:
	    isolated_list.append(q)
	    print "lista con poligonos aislados "
	    print isolated_list
	#listar en pantalla los poligonos aislados
	print "lista con poligonos aislados "
	print isolated_list
    
    ################################
    #colocar en primer lugar aquellos isolated
    if len(isolated_list) >0:
	b=0
	c=0
	while b<len(isolated_list):
	    c=int(isolated_list[b])
	    cat_no_river_sorted.remove(c)
	    b+=1
	cat_no_river_sorted = isolated_list+cat_no_river_sorted
    print "Lista de cat ordenados"
    print cat_no_river_sorted
    ################################
    z=0
    for i in cat_no_river_sorted:
    #for i in [770,2373,23,88,381,1500,380]:
    #2373 inicia bien pero queda en un boucle, 770 esta bien:
    #for i in [23] inicia como boucle:
    #for i in [88] inicia bien pero termina en una falsa depresion la bypasea:
    #for i in [381] flasa depresion:
    #for i in [1500] falsa derpesion:
    #for i in [380] flasa depresion:
	print i
	aux=i
	#inicializar caminio minimo
	path_list=[i]
	boucle_list=[]
	b=0
	while list_polygons_river_sorted.count(i) ==0:
	    #listar vecinos de columna left id_mesh_a
	    condition_id_mesh_b = "id_mesh_b="+str(i)
	    neig_a =grass.read_command("v.db.select",map=wti_v1,col='id_mesh_a',flags='c',where=condition_id_mesh_b)
	    neig_a2=neig_a.rsplit()
	    neig_a3=sorted(neig_a2)
	    a=0
	    b=0
	    c=0
	    list=[]
	    #Delete repeted values
	    print neig_a3
	    while b<len(neig_a3):
		c=int(neig_a3[b])
		if list.count(c) ==0 and boucle_list.count(c) ==0:
		    list.append(c)
		    print "Added "+ str(c)
		else :
		    print "Repeted Value "+ str(c)
		b+=1
	    sorted_neig=sorted(list)
	    print sorted_neig
	    
	    #listar vecinos de columna rigth id_mesh_b
	    condition_id_mesh_a = "id_mesh_a="+str(i)
	    neig_b =grass.read_command("v.db.select",map=wti_v1,col='id_mesh_b',flags='c',where=condition_id_mesh_a)
	    neig_b2=neig_b.rsplit()
	    neig_b3=sorted(neig_b2)
	    a=0
	    b=0
	    c=0
	    #Delete repeted values
	    print neig_b3
	    while b<len(neig_b3):
		c=int(neig_b3[b])
		if sorted_neig.count(c) ==0 and boucle_list.count(c) ==0:
		    sorted_neig.append(c)
		    print "Added "+ str(c)
		else :
		    print "Repeted Value "+ str(c)
		b+=1
	    sorted_neig_b=sorted(sorted_neig)
	    print sorted_neig_b
	    #borrar elementos con -1 que no tienen vecino
	    if sorted_neig_b.count(-1) >0:
		    sorted_neig_b.remove(-1)
		    print "Removed neig -1 "
	    

	    
	    
	    #crear lista con alturas de cada uno
	    a=0
	    b=0
	    c=0
	    alt_list=[]
	    #agregar cada altura segun cat
	    while b<len(sorted_neig_b):
		c=int(sorted_neig_b[b])
		cat_query = "id_mesh="+str(c)
		alt=grass.read_command("v.db.select",map=model_mesh,col=column_alt,flags='c',where=cat_query)
		alt2=alt.rsplit()
		alt3=float(alt2[0])
		alt_list.append(alt3)
		b+=1
	    print alt_list
	    #verificar que no se hayan acabado los vecinos
	    if len(alt_list)==0:
		print "estoy en un agujero"
		false_depresion_list.append(i)
		list_polygons_river_sorted.append(i)
		path_list=[]
	    if len(alt_list)>0:
	       #encontrar camino minimo hacia el rio
		alt_sorted=sorted(alt_list)
		min1=alt_sorted[0]
		b=0
		cat_min=0
		while b<len(alt_list):
		    if min1==alt_list[b]:	
			cat_min= sorted_neig_b[b]
			print "cat related alt min : " + str(sorted_neig_b[b]) + " ;  alt min : " +str(alt_list[b])
			path_list.append(sorted_neig_b[b])
			print "::: Path List :::"
			print path_list
			if path_list.count(sorted_neig_b[b])<=1:
			    i=sorted_neig_b[b]
			if path_list.count(sorted_neig_b[b])>1 and len(path_list)>3:
			    print "There is a Boucle"
			    #boucle_list.append(sorted_neig_b[b])
			    #path_list=path_list[0:len(path_list)-3]
			    boucle_list.append(path_list[len(path_list)-2])
			    path_list=path_list[0:len(path_list)-2]
			    print ":::: Path List ::::"
			    print path_list
			    print ":::: Boucle List ::::"
			    print boucle_list
			    i=path_list[len(path_list)-1]
			    print "nuevo punto de iteracion  " + str(i)
			if path_list.count(sorted_neig_b[b])>1 and len(path_list)==3:
			    print "There is a Boucle at the starting of the iteration"
			    boucle_list.append(path_list[len(path_list)-2])
			    path_list=path_list[0:len(path_list)-2]
			    print ":::: Path List ::::"
			    print path_list
			    print ":::: Boucle List ::::"
			    print boucle_list
			    i=path_list[len(path_list)-1]
			    print "nuevo punto de iteracion  " + str(i)
			b=len(alt_list)
		    else:
			print "cat : " + str(sorted_neig_b[b]) + " ; alt : " +str(alt_list[b])
			b+=1
	#Generar la polilinea de los path way
	if len(alt_list)==0:
	    b=1
	else:
	    b=0
	while b<len(path_list)-1:
	    cat1="poly_"+str(path_list[b])
	    cat2="poly_"+str(path_list[b+1])
	    where_sql='id_mesh='+str(path_list[b])
	    grass.run_command("v.extract",input=model_mesh,where=where_sql,output=cat1,overwrite=True)
	    where_sql='id_mesh='+str(path_list[b+1])
	    grass.run_command("v.extract",input=model_mesh,where=where_sql,output=cat2,overwrite=True)
	    distance_i="dist_"+str(b)
	    grass.run_command("v.distance",_from=cat1,to=cat2,out='dist_temp_olaf',from_type='centroid', to_type='centroid',upload='dist',column='dist',flags='p',overwrite=True)
	    grass.run_command("v.db.addtable",map='dist_temp_olaf', columns='id int,id_polyg int,id_connect int,con_type varchar(15)')
	    grass.run_command("v.category",input='dist_temp_olaf',output=distance_i,option='add',overwrite=True)
	    grass.run_command("v.to.db", map=distance_i,option='cat')
	    id_polyg_cat=str(path_list[b])
	    grass.run_command("v.db.update",map=distance_i,column='id_polyg',value=id_polyg_cat)
	    grass.run_command("v.db.update",map=distance_i,column='con_type',value="poly")
	    id_connect_cat=str(path_list[b+1])
	    grass.run_command("v.db.update",map=distance_i,column='id_connect',value=id_connect_cat)	    
	    grass.run_command("g.remove",vect=cat1)
	    grass.run_command("g.remove",vect=cat2)
	    if b==0:
		grass.run_command("g.copy",vect='dist_0,distance_temp',overwrite=True)
		grass.run_command("g.remove",vect='dist_0')
		b+=1
	    else:
		patch="distance_temp,"+distance_i
		print "orden de patch " + patch
		grass.run_command("v.patch", input=patch, output='distance_complete', overwrite=True,flags='e')
		print "ejecute patch "
		grass.run_command("g.copy",vect='distance_complete,distance_temp', overwrite=True)
		grass.run_command("g.remove",vect=distance_i)
		b+=1
	
	
	if z==0 and len(alt_list)!=0:
	    copy="distance_temp,olaf_total_temp_1"
	    grass.run_command("g.copy",vect=copy,overwrite=True)
	    z+=1
	if z>0 and len(alt_list)!=0:
	    olaf_i="olaf_from_"+str(aux)+"_to_"+str(path_list[len(path_list)-1])
	    copy="distance_temp,"+olaf_i
	    grass.run_command("g.copy",vect=copy,overwrite=True)
	    patch="olaf_total_temp_1,"+olaf_i
	    grass.run_command("v.patch", input=patch, output='olaf_total_temp_2', overwrite=True,flags='e')
	    grass.run_command("g.copy",vect='olaf_total_temp_2,olaf_total_temp_1', overwrite=True)
	    grass.run_command("g.remove",vect=olaf_i)
	    z+=1
	
	    
	list_polygons_river_sorted+= path_list
	print "lista de poligonos rios es"
	print list_polygons_river_sorted
	print "lista de poligonos que estan o que llegan a falsas depresiones"
	print false_depresion_list
    
    #generar el mapa vectorial OLAF por subbcuenca
    copy_sbb_i="olaf_total_temp_2,olaf_sbb_"+str(s)
    grass.run_command("g.copy",vect=copy_sbb_i, overwrite=True)
    
    
    
    #generar mapa con depresiones
    if len(false_depresion_list)>0:
	l=0
	for i in false_depresion_list:
	    if l==0:
		where_sql_l='id_mesh='+str(i)
		grass.run_command("v.extract",input=model_mesh,where=where_sql_l,output='false_poly_1',overwrite=True)
		l+=1
	    else:
		where_sql_l='id_mesh='+str(i)
		grass.run_command("v.extract",input=model_mesh,where=where_sql_l,output='false_poly_2',overwrite=True)
		grass.run_command("v.patch", input="false_poly_1,false_poly_2", output='false_poly_3', overwrite=True,flags='e')
		grass.run_command("g.copy",vect='false_poly_3,false_poly_1', overwrite=True)
		grass.run_command("g.remove",vect='false_poly_3,false_poly_2')
		l+=1
	false_i="false_poly_1,false_depresion_sbb"+str(s)
	grass.run_command("g.copy",vect=false_i, overwrite=True)
	subb_with_false_depresion.append(s)







for s in subb_count_sorted:
#for s in [12]:
    subb_i="olaf_sbb_"+str(s)
    grass.run_command("v.db.update",map=subb_i,column='id',value='cat')
    print "actualizado valores de sbb = " + subb_i
    copy_sbb_i=subb_i+","+subb_i+"_initial"
    grass.run_command("g.copy",vect=copy_sbb_i, overwrite=True)




#eliminar tramos de OLAF repetidos
for s in subb_count_sorted:
#for s in [12]:
    subb_i="olaf_sbb_"+str(s)
    print subb_i
    #grass.run_command("v.db.update",map=subb_i,column='id',value='cat')
    grass.run_command("v.db.addcol",map=subb_i,column='id_diss int')
    grass.run_command("v.db.update",map=subb_i,column='id_diss',value='id_connect*id_polyg')
    id_diss_count=grass.read_command("v.db.select",map=subb_i,col='id_diss',flags='c')
    id_diss_count2=id_diss_count.rsplit()
    id_diss_count3=sorted(id_diss_count2)
    #inicializar variables auxiliares
    print "lista con valores repetidos"
    print id_diss_count3
    x=0
    list_id_diss=[]
    list_deleted=[]
    print str(x)
    
    #Delete repeted values
    while x<len(id_diss_count3):
	c=int(id_diss_count3[x])
	print "c = "+str(c)
	if list_id_diss.count(c) ==0:
	    list_id_diss.append(c) 
	else:
	    if list_deleted.count(c) ==0:
		print "Repeted Segment = "+ str(c)
		where_sql1="id_diss="+str(c)
		id_diss_list=grass.read_command("v.db.select",map=subb_i,col='id',flags='c',where=where_sql1)
		id_diss_list2=id_diss_list.rsplit()
		id_diss_list3=float(id_diss_list2[0])
		where_sql2="id_diss="+str(c)
		grass.run_command("v.extract",input=subb_i,where=where_sql2,output='subb_temp1',overwrite=True,flags='r')
		where_sql3="id="+str(id_diss_list3)
		grass.run_command("v.extract",input=subb_i,where=where_sql3,output='subb_temp2',overwrite=True)
		patch="subb_temp1,subb_temp2"
		print "orden de patch " + patch
		grass.run_command("v.patch", input=patch,output=subb_i, overwrite=True,flags='e')
		#Agregar indice de los borrados
		list_deleted.append(c)
		print list_deleted
	    else:
		print "Ya se borro! c = "+str(c)
	x+=1
    #grass.run_command("v.db.dropcol",map=model_mesh,columns='id_temp int')

print "FALSE DEPRESIONS POLYGONS"
print false_depresion_list
print "ISOLATED POLYGONS"
print isolated_list

#UNIR TODOS LOS POLIGONOS CON FALSAS DEPRESIONES
n=0
if len(subb_with_false_depresion)>0:
    for t in subb_with_false_depresion:
	if n == 0:
	    copy_rule="false_depresion_sbb"+str(t)+",false_drepresion_polygons_1"
	    grass.run_command("g.copy",vect=copy_rule, overwrite=True)
	    remove_t="false_depresion_sbb"+str(t)
	    grass.run_command("g.remove",vect=remove_t)
	    n+=1
	else:
	    patch_rule="false_depresion_sbb"+str(t)+",false_drepresion_polygons_1"
	    grass.run_command("v.patch", input=patch_rule,output='drepresion_polygons_2', overwrite=True,flags='e')
	    copy_rule="drepresion_polygons_2,false_drepresion_polygons_1"
	    grass.run_command("g.copy",vect=copy_rule, overwrite=True)
	    remove_t="false_depresion_sbb"+str(t)
	    grass.run_command("g.remove",vect=remove_t)




#UNIR TODOS LOS VECTORES OLAF
n=0
for t in subb_count_sorted:
    if n == 0:
	copy_rule="olaf_sbb_"+str(t)+",olaf_temp_total_1"
	grass.run_command("g.copy",vect=copy_rule, overwrite=True)
	remove_t="olaf_sbb_"+str(t)
	grass.run_command("g.remove",vect=remove_t)
	remove_t2="olaf_sbb_"+str(t)+"_initial"
	grass.run_command("g.remove",vect=remove_t2)
	n+=1
    else:
	patch_rule="olaf_sbb_"+str(t)+",olaf_temp_total_1"
	grass.run_command("v.patch", input=patch_rule,output='olaf_temp_total_2', overwrite=True,flags='e')
	copy_rule="olaf_temp_total_2,olaf_temp_total_1"
	grass.run_command("g.copy",vect=copy_rule, overwrite=True)
	remove_t="olaf_sbb_"+str(t)
	grass.run_command("g.remove",vect=remove_t)
	remove_t2="olaf_sbb_"+str(t)+"_initial"
	grass.run_command("g.remove",vect=remove_t2)
    





grass.run_command("g.remove",vect="dist_temp,dist_temp_olaf,olaf_temp_total_2,distance_complete,distance_temp,olaf_total_temp_1,drepresion_polygons_2,olaf_total_temp_2,poly_to_river_temp_2,subb_temp1,false_poly_1,subb_temp2,wti_sbb_temp")
grass.run_command("v.db.dropcol",map='olaf_temp_total_1',column='id_diss')
grass.run_command("v.patch", input='olaf_temp_total_1,poly_to_river_temp_1', output="olaf_output_temp", overwrite=True,flags='e')

#exportar e importar para limpieza topologica topologia
grass.run_command("v.out.ogr",input="olaf_output_temp",type='line',dsn="olaf_folder",flags='e',overwrite=True)


folder=directory+"/olaf_folder/olaf_output_temp.shp"
grass.run_command("v.in.ogr",dsn=folder,output=olaf_output_vector,flags='o',overwrite=True)

grass.run_command("v.db.update",map=olaf_output_vector,column='id',value='cat')
grass.run_command("v.db.dropcol",map=olaf_output_vector,column='cat_')
grass.run_command("v.out.ogr", input=olaf_output_vector, layer=1, dsn=olaf_output_vector, overwrite=True)

folder_rm=directory+"/olaf_folder"
if os.path.exists(folder_rm): 
    shutil.rmtree(folder_rm)
    print "se borro"

grass.run_command("g.remove",vect='olaf_temp_total_1,poly_to_river_temp_1,olaf_output_temp')


 
    
    
    
    





