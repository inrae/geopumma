#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.all_interfaces.py
# AUTHOR(S)     : Sanzana P. 01/12/2014
# BASED FROM  	: Florent B. 10/01/2011 interOLAF.py
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
import grass.script as grass
env = grass.gisenv()
print env

#1.-imprimir vectores disponibles y definir nombre de polygonos





#2.-Generar lista con poligonos vecinos al rio
polygons_river=grass.read_command("v.db.select",map='wtri_final_v1',col='id_plot',flags='c')
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



#Unir poligonos al rio
#a=0
#for i in list_polygons_river_sorted:
#    cat1="poly_"+str(i)
#    where_sql='cat='+str(i)
#    grass.run_command("v.extract",input='los_guindos_mesh_v12',where=where_sql,output=cat1,overwrite=True)
#    distance_i="dist_"+str(i)
#    grass.run_command("v.distance",_from=cat1,to='wtri_final_v1',out=distance_i,from_type='centroid', to_type='line',upload='dist',column='dist',flags='p',overwrite=True)
#    if a==0:
#	copy=distance_i+",poly_to_river_temp_1"
#	grass.run_command("g.copy",vect=copy,overwrite=True)
#	grass.run_command("g.remove",vect=distance_i)
#	grass.run_command("g.remove",vect=cat1)
#	a+=1
#    else:
#	patch="poly_to_river_temp_1,"+distance_i
#	grass.run_command("v.patch", input=patch, output='poly_to_river_temp_2', overwrite=True)
#	grass.run_command("g.copy",vect='poly_to_river_temp_2,poly_to_river_temp_1', overwrite=True)
#	grass.run_command("g.remove",vect=distance_i)
#	grass.run_command("g.remove",vect=cat1)
#	a+=1

    


#Buscar vecinos para cada subcuenca

subb_count = grass.read_command("v.db.select",map='los_guindos_mesh_v12',col='id_subb_2',flags='c')
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

for s in subb_count_sorted:
    subb_query='id_subb_2='+str(s)
    polygons_count = grass.read_command("v.db.select",map='los_guindos_mesh_v12',col='cat',flags='c', where=subb_query)
    polygons_count2=polygons_count.rsplit()
    polygons_count3=sorted(polygons_count2)
    
    x=0
    cat_no_river=[]
    false_depresion_list=[]
    
    #conservar solo valores que no estan cercanos al rio
    while x<len(polygons_count3):
	c=int(polygons_count3[x])
	if list_polygons_river_sorted.count(c) ==0:
	    cat_no_river.append(c) 
	else :
	    print "Repeted Value "+ str(c)
	x+=1
    cat_no_river_sorted=sorted(cat_no_river)
    
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
	    #listar vecinos de columna left id_a
	    condition_id_b = "id_b="+str(i)
	    neig_a =grass.read_command("v.db.select",map='wti_final_v1',col='id_a',flags='c',where=condition_id_b)
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
	    
	    #listar vecinos de columna left id_b
	    condition_id_a = "id_a="+str(i)
	    neig_b =grass.read_command("v.db.select",map='wti_final_v1',col='id_b',flags='c',where=condition_id_a)
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
	    
	    #borrar aquellos que ya fueron visados 
	    
	    
	    #crear lista con alturas de cada uno
	    a=0
	    b=0
	    c=0
	    alt_list=[]
	    #agregar cada altura segun cat
	    while b<len(sorted_neig_b):
		c=int(sorted_neig_b[b])
		cat_query = "cat="+str(c)
		alt=grass.read_command("v.db.select",map='los_guindos_mesh_v12',col='alt',flags='c',where=cat_query)
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
	    where_sql='cat='+str(path_list[b])
	    grass.run_command("v.extract",input='los_guindos_mesh_v12',where=where_sql,output=cat1,overwrite=True)
	    where_sql='cat='+str(path_list[b+1])
	    grass.run_command("v.extract",input='los_guindos_mesh_v12',where=where_sql,output=cat2,overwrite=True)
	    distance_i="dist_"+str(b)
	    grass.run_command("v.distance",_from=cat1,to=cat2,out=distance_i,from_type='centroid', to_type='centroid',upload='dist',column='dist',flags='p',overwrite=True)
	    grass.run_command("g.remove",vect=cat1)
	    grass.run_command("g.remove",vect=cat2)
	    if b==0:
		grass.run_command("g.copy",vect='dist_0,distance_temp',overwrite=True)
		grass.run_command("g.remove",vect='dist_0')
		b+=1
	    else:
		patch="distance_temp,"+distance_i
		print "orden de patch " + patch
		grass.run_command("v.patch", input=patch, output='distance_complete', overwrite=True)
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
	    grass.run_command("v.patch", input=patch, output='olaf_total_temp_2', overwrite=True)
	    grass.run_command("g.copy",vect='olaf_total_temp_2,olaf_total_temp_1', overwrite=True)
	    grass.run_command("g.remove",vect=olaf_i)
	    z+=1
	
	    
	list_polygons_river_sorted+= path_list
	print "lista de polygonos rios es"
	print list_polygons_river_sorted
	print "lista de poligonos que estan o que llegan a falsas depresiones"
	print false_depresion_list
    copy_s="olaf_total_temp_2,olaf_sbb_"+str(s)
    grass.run_command("g.copy",vect=copy_s, overwrite=True)

    








