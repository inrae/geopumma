#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.convexity_segmentation.py
# AUTHOR(S)     : Sanzana P. 01/12/2014
# BASED ON  	: convexity.py Sanzana P. 10/01/2011
#               
# PURPOSE       : Dissolving by convexity criteria segmentation
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
directory = os.getcwd()
print directory
import os.path
import shutil
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygon to dissolve : ")
polygons_out=raw_input("Please enter the name of the output polygon : ")
polygons_columns=raw_input("Please enter the name of polygon pre Triangle to get columns: ")
CIT_text=raw_input("Please enter the Convexity Index Threshold (CIT 0.75-0.85) : ")
CIT=float(CIT_text)
#CIT=0.750
A_MAX_T_text=raw_input("Please enter the Maximum Area (Amin rec = 20000 m2) : ")
A_MAX_T=float(A_MAX_T_text)
#MIN_A_T=500
FF_MIN_T_text=raw_input("Please enter the Form Factor Threshold (FFT 0.20-0.40) : ")
FF_MIN_T=float(FF_MIN_T_text)
#FF_MIN_T=0.20
snap=0.001
#dissolve=raw_input("Dissolve small areas: Yes (1) or Not (0): ")
grass.run_command("g.remove",vect='new_points,new_set_disolved,out_poly_1,polygons_temp,polygons_temp_1,polygons_temp_1_table,poly_hull,polygons_total_1,polygons_total_2')

#add table and calculate areas
grass.run_command("v.db.addtable",map=polygons)
grass.run_command("v.db.addcol",map=polygons,col='area double')
grass.run_command("v.db.addcol",map=polygons,col='peri double')
grass.run_command("v.db.addcol",map=polygons,col='convexity double')
grass.run_command("v.to.db",map=polygons,col='area',option='area')
grass.run_command("v.to.db",map=polygons,col='peri',option='perimeter')


#add column to identify new set of polygons
grass.run_command("v.db.dropcol",map=polygons,col='new_set')
grass.run_command("v.db.addcol",map=polygons,col='new_set int')
grass.run_command("v.db.update",map=polygons,col='new_set',value='cat')



#sort list the categories, without repeted values
category=grass.read_command("v.db.select",map=polygons,col='id_mesh',flags='c')
cat2=category.rsplit()
cat3=sorted(cat2)
x=0
list=[]


#Delete repeted values
print cat3
while x<len(cat3):
    z=int(cat3[x])
    if list.count(z)==0:
        list.append(z)
    else :
        print "Repeted Value "+ str(z)
    x+=1
list_sorted=sorted(list)


######################################################
######################################################



#extract polygons to start dissolve rule
t=0
for i in list_sorted:
    where_sql_1="id_mesh="+str(i)
    grass.run_command("v.extract",input=polygons,output='out_poly_1',where=where_sql_1,overwrite=True)
    #find neigbords polygons to boundaries in layer 2
    grass.run_command("v.category",input='out_poly_1',out='polygons_temp',layer='2',type='boundary',option='add',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp',layer='2',col='left integer,right integer')
    grass.run_command("v.to.db", map='polygons_temp',option='sides',col='left,right',layer='2')
    
    
    #define area minim threshold
    grass.run_command("v.extract",input=polygons,output='out_poly_area_1',where=where_sql_1,overwrite=True)
    grass.run_command("v.dissolve",input='out_poly_area_1',output='out_poly_area_1_disolved',column='id_mesh',overwrite=True)
    grass.run_command("v.db.addtable",map='out_poly_area_1_disolved')
    grass.run_command("v.db.addcol",map='out_poly_area_1_disolved',col='area double')
    grass.run_command("v.to.db",map='out_poly_area_1_disolved',col='area',option='area')
    area_list_min=grass.read_command("v.db.select",map='out_poly_area_1_disolved',col='area',flags='c')
    area_list_min1=area_list_min.rsplit()
    area_list_min2 = map(float, area_list_min1)
    
    if area_list_min2[0]*0.01<10:
        MIN_A_T=10
    else:
        MIN_A_T=area_list_min2[0]*0.01
    
    
    
    
    
    
    #extract list with area value
    area_list=grass.read_command("v.db.select",map='polygons_temp',col='area',flags='c')
    area_list1=area_list.rsplit()
    area_list2 = map(float, area_list1)

    min1=min(area_list2)
    print "minimo " + str(min1)
    max1=max(area_list2)
    print "maximo " + str(max1)
    
    #category list
    cat_list=grass.read_command("v.db.select",map='polygons_temp',col='cat',flags='c')
    cat_list1=cat_list.rsplit()
    cat_list2 = map(int, cat_list1)
        
    length=len(cat_list2)
    #iniciar busqueda de maximos vecinos
    #while length > 1 :
    temp=1
    #iniciar auxiliar que disuelve
    aux_new_set=cat_list2[area_list2.index(max1)]
    while length>1:
        print "################### INICIA EL WHILE####################"
        #buscar categoria asociada al area maxima
        cat_max=cat_list2[area_list2.index(max1)]
        print "inicia en cat max : " + str(cat_max)
        #borrar categoria y area del listado de checkeados
        cat_list2.remove(cat_max)
        area_list2.remove(max1)
        
        
        #asignar valor de new_set en area maxima
        where_sql_cat_max="cat="+str(cat_max)
        grass.run_command("v.db.update",map='polygons_temp',column='new_set',value=aux_new_set, where=where_sql_cat_max)
        
        #buscar categorias de los vecinos del area maxima
        where_sql_left="right="+str(cat_max)
        neig_left=grass.read_command("v.db.select",map='polygons_temp',col='left',flags='c',layer=2,where=where_sql_left)
        neig_left1=map(int, neig_left.rsplit())
        where_sql_right="left="+str(cat_max)
        neig_right=grass.read_command("v.db.select",map='polygons_temp',col='right',flags='c',layer=2,where=where_sql_right)
        neig_right1=map(int, neig_right.rsplit())
        neig=neig_left1+neig_right1
        print "vecinos"
        print neig
        #borrar de cat repetidos, con valor de  -1 y aquellos que no han sido chequeados
        x=0
        cat_neig=[]
        #Delete repeted values
        while x<len(neig):
            z=neig[x]
            if cat_neig.count(z)==0 and z!=-1 and cat_list2.count(z)>0 :
                
                cat_neig.append(z)
            else :
                print "Repeted Value "+ str(z)
            x+=1
        print "categorias sin -1 y repetidos"
        print cat_neig
        
        #en caso que lista de vecinos este vacia se para la iteracion
        if len(cat_neig)>0:

            #area vecinos
            m=0
            area_neig=[]
            for n in cat_neig:
                area_neig.append(area_list2[cat_list2.index(n)])
            print "area asociada a cada cat"
            print area_neig
            
            #seleccionar el area maxima vecina
            
            a_max_neig_1=max(area_neig)
            print "area maxima " + str(a_max_neig_1)
            
            cat_max_neig_1=cat_neig[area_neig.index(a_max_neig_1)]
            
            print "categoria con a max"
            print cat_max_neig_1
            
            
            
            #chequear nuevo indice de convexidad
            where_sql_extract="new_set="+str(aux_new_set)+" OR cat="+str(cat_max_neig_1)
            grass.run_command("v.extract",input='polygons_temp',output='convex_test',where=where_sql_extract,overwrite=True)
            grass.run_command("v.db.addcol",map='convex_test',col='id_temp int')
            grass.run_command("v.db.update",map='convex_test',column='id_temp',value=1)
            grass.run_command("v.dissolve",input='convex_test',output='new_set_disolved',column='id_temp',overwrite=True)
            grass.run_command("v.db.addtable",map='new_set_disolved')
            grass.run_command("v.db.addcol",map='new_set_disolved',col='peri double')
            grass.run_command("v.to.db",map='new_set_disolved',col='peri',option='perimeter')
            grass.run_command("g.region",vect=polygons)
            grass.run_command("v.to.points",input='convex_test',output='new_points',overwrite=True,flags='v')
            grass.run_command("v.hull",input='new_points',output='poly_hull',overwrite=True,flags='a')
            grass.run_command("v.db.addtable",map='poly_hull')
            grass.run_command("v.db.addcol",map='poly_hull',col='periH double')
            grass.run_command("v.to.db",map='poly_hull',col='periH',option='perimeter')
            hperi=grass.read_command("v.db.select",map='poly_hull',col='periH',flags='c')
            hperi1=hperi.rsplit()
            hperi2=hperi1[0]
            hperi3=float(hperi2)
            peri=grass.read_command("v.db.select",map='new_set_disolved',col='peri',flags='c')
            peri1=peri.rsplit()
            peri2=peri1[0]
            peri3=float(peri2)
            convexity=hperi3/peri3
            print "####################################nueva convexidad############################"
            print convexity
            new_area=a_max_neig_1+max1
            
            if convexity>CIT and new_area<A_MAX_T:
                #actualizar poligono inicial
                where_sql_cat_max="cat="+str(cat_max_neig_1)
                grass.run_command("v.db.update",map='out_poly_1',col='new_set',value=aux_new_set,where=where_sql_cat_max)
                
                #asignar valor de new_set en area maxima
                where_sql_cat_max="cat="+str(cat_max_neig_1)
                grass.run_command("v.db.update",map='polygons_temp',column='new_set',value=aux_new_set, where=where_sql_cat_max)
                grass.run_command("v.dissolve",input='polygons_temp',output='polygons_temp_1',column='new_set',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_1')
                grass.run_command("v.db.addcol",map='polygons_temp_1',col='area double')
                grass.run_command("v.to.db",map='polygons_temp_1',col='area',option='area')
                grass.run_command("v.db.addcol",map='polygons_temp_1',col='new_set int')
                grass.run_command("v.db.update",map='polygons_temp_1',column='new_set',value='cat')
                grass.run_command("g.copy", vect='polygons_temp_1,polygons_temp_2', overwrite=True)
                
                #find neigbords polygons to boundaries in layer 2
                grass.run_command("v.category",input='polygons_temp_2',out='polygons_temp_3',layer='2',type='boundary',option='add',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_3',layer='2',col='left integer,right integer')
                grass.run_command("v.to.db", map='polygons_temp_3',option='sides',col='left,right',layer='2')
                #extract list with area value
                
                #extract list with area value
                area_list=grass.read_command("v.db.select",map='polygons_temp_3',col='area',flags='c')
                area_list1=area_list.rsplit()
                area_list2 = map(float, area_list1)
                if len(area_list2)==0:
                    break
                min1=min(area_list2)
                print "minimo " + str(min1)
                max1=max(area_list2)
                print "maximo " + str(max1)
                
                #category list
                cat_list=grass.read_command("v.db.select",map='polygons_temp_3',col='cat',flags='c')
                cat_list1=cat_list.rsplit()
                cat_list2 = map(int, cat_list1)
                
                grass.run_command("g.remove", vect='polygons_temp',flags='f')
                grass.run_command("db.droptable",table='polygons_temp_1',flags='f')
                grass.run_command("g.copy", vect='polygons_temp_3,polygons_temp', overwrite=True)
            
            
            if convexity<=CIT or new_area>=A_MAX_T:
                print "convexidad no cumple"
                where_sql_cat_max="cat="+str(aux_new_set)
                grass.run_command("v.extract",input='polygons_temp',output='polygons_temp_4',where=where_sql_cat_max,flags='r',overwrite=True)
                
                #find neigbords polygons to boundaries in layer 2
                grass.run_command("v.category",input='polygons_temp_4',out='polygons_temp_5',layer='2',type='boundary',option='add',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_5',layer='2',col='left integer,right integer')
                grass.run_command("v.to.db", map='polygons_temp_5',option='sides',col='left,right',layer='2')
                #extract list with area value
                
                #extract list with area value
                area_list=grass.read_command("v.db.select",map='polygons_temp_5',col='area',flags='c')
                area_list1=area_list.rsplit()
                area_list2 = map(float, area_list1)
            
                min1=min(area_list2)
                print "minimo " + str(min1)
                max1=max(area_list2)
                print "maximo " + str(max1)
                
                #category list
                cat_list=grass.read_command("v.db.select",map='polygons_temp_5',col='cat',flags='c')
                cat_list1=cat_list.rsplit()
                cat_list2 = map(int, cat_list1)
                
                grass.run_command("g.remove", vect='polygons_temp',flags='f')
                grass.run_command("g.copy", vect='polygons_temp_5,polygons_temp', overwrite=True)
                
                #actualizar nuevo new_set_aux
                aux_new_set=cat_list2[area_list2.index(max1)]
        
    break



######################################################
######################################################




#extract polygons to start dissolve rule
t=0
for i in list_sorted:
#for i in [2703,3099]:
    where_sql_1="id_mesh="+str(i)
    grass.run_command("v.extract",input=polygons,output='out_poly_1',where=where_sql_1,overwrite=True)
    #find neigbords polygons to boundaries in layer 2
    grass.run_command("v.category",input='out_poly_1',out='polygons_temp',layer='2',type='boundary',option='add',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp',layer='2',col='left integer,right integer')
    grass.run_command("v.to.db", map='polygons_temp',option='sides',col='left,right',layer='2')
    
    
    #define area minim threshold
    grass.run_command("v.extract",input=polygons,output='out_poly_area_1',where=where_sql_1,overwrite=True)
    grass.run_command("v.dissolve",input='out_poly_area_1',output='out_poly_area_1_disolved',column='id_mesh',overwrite=True)
    grass.run_command("v.db.addtable",map='out_poly_area_1_disolved')
    grass.run_command("v.db.addcol",map='out_poly_area_1_disolved',col='area double')
    grass.run_command("v.to.db",map='out_poly_area_1_disolved',col='area',option='area')
    area_list_min=grass.read_command("v.db.select",map='out_poly_area_1_disolved',col='area',flags='c')
    area_list_min1=area_list_min.rsplit()
    area_list_min2 = map(float, area_list_min1)
    
    if area_list_min2[0]*0.01<10:
        MIN_A_T=10
    else:
        MIN_A_T=area_list_min2[0]*0.01
    
    
    
    
    
    
    #extract list with area value
    area_list=grass.read_command("v.db.select",map='polygons_temp',col='area',flags='c')
    area_list1=area_list.rsplit()
    area_list2 = map(float, area_list1)

    min1=min(area_list2)
    print "minimo " + str(min1)
    max1=max(area_list2)
    print "maximo " + str(max1)
    
    #category list
    cat_list=grass.read_command("v.db.select",map='polygons_temp',col='cat',flags='c')
    cat_list1=cat_list.rsplit()
    cat_list2 = map(int, cat_list1)
        
    length=len(cat_list2)
    #iniciar busqueda de maximos vecinos
    #while length > 1 :
    temp=1
    #iniciar auxiliar que disuelve
    aux_new_set=cat_list2[area_list2.index(max1)]
    while length>1:
        print "################### INICIA EL WHILE####################"
        #buscar categoria asociada al area maxima
        cat_max=cat_list2[area_list2.index(max1)]
        print "inicia en cat max : " + str(cat_max)
        #borrar categoria y area del listado de checkeados
        cat_list2.remove(cat_max)
        area_list2.remove(max1)
        
        
        #asignar valor de new_set en area maxima
        where_sql_cat_max="cat="+str(cat_max)
        grass.run_command("v.db.update",map='polygons_temp',column='new_set',value=aux_new_set, where=where_sql_cat_max)
        
        #buscar categorias de los vecinos del area maxima
        where_sql_left="right="+str(cat_max)
        neig_left=grass.read_command("v.db.select",map='polygons_temp',col='left',flags='c',layer=2,where=where_sql_left)
        neig_left1=map(int, neig_left.rsplit())
        where_sql_right="left="+str(cat_max)
        neig_right=grass.read_command("v.db.select",map='polygons_temp',col='right',flags='c',layer=2,where=where_sql_right)
        neig_right1=map(int, neig_right.rsplit())
        neig=neig_left1+neig_right1
        print "vecinos"
        print neig
        #borrar de cat repetidos, con valor de  -1 y aquellos que no han sido chequeados
        x=0
        cat_neig=[]
        #Delete repeted values
        while x<len(neig):
            z=neig[x]
            if cat_neig.count(z)==0 and z!=-1 and cat_list2.count(z)>0 :
                
                cat_neig.append(z)
            else :
                print "Repeted Value "+ str(z)
            x+=1
        print "categorias sin -1 y repetidos"
        print cat_neig
        
        #en caso que lista de vecinos este vacia se para la iteracion
        if len(cat_neig)>0:

            #area vecinos
            m=0
            area_neig=[]
            for n in cat_neig:
                area_neig.append(area_list2[cat_list2.index(n)])
            print "area asociada a cada cat"
            print area_neig
            
            #seleccionar el area maxima vecina
            
            a_max_neig_1=max(area_neig)
            print "area maxima " + str(a_max_neig_1)
            
            cat_max_neig_1=cat_neig[area_neig.index(a_max_neig_1)]
            
            print "categoria con a max"
            print cat_max_neig_1
            
            
            
            #chequear nuevo indice de convexidad
            where_sql_extract="new_set="+str(aux_new_set)+" OR cat="+str(cat_max_neig_1)
            grass.run_command("v.extract",input='polygons_temp',output='convex_test',where=where_sql_extract,overwrite=True)
            grass.run_command("v.db.addcol",map='convex_test',col='id_temp int')
            grass.run_command("v.db.update",map='convex_test',column='id_temp',value=1)
            grass.run_command("v.dissolve",input='convex_test',output='new_set_disolved',column='id_temp',overwrite=True)
            grass.run_command("v.db.addtable",map='new_set_disolved')
            grass.run_command("v.db.addcol",map='new_set_disolved',col='peri double')
            grass.run_command("v.to.db",map='new_set_disolved',col='peri',option='perimeter')
            grass.run_command("g.region",vect=polygons)
            grass.run_command("v.to.points",input='convex_test',output='new_points',overwrite=True,flags='v')
            grass.run_command("v.hull",input='new_points',output='poly_hull',overwrite=True,flags='a')
            grass.run_command("v.db.addtable",map='poly_hull')
            grass.run_command("v.db.addcol",map='poly_hull',col='periH double')
            grass.run_command("v.to.db",map='poly_hull',col='periH',option='perimeter')
            hperi=grass.read_command("v.db.select",map='poly_hull',col='periH',flags='c')
            hperi1=hperi.rsplit()
            hperi2=hperi1[0]
            hperi3=float(hperi2)
            peri=grass.read_command("v.db.select",map='new_set_disolved',col='peri',flags='c')
            peri1=peri.rsplit()
            peri2=peri1[0]
            peri3=float(peri2)
            convexity=hperi3/peri3
            print "####################################nueva convexidad############################"
            print convexity
            new_area=a_max_neig_1+max1
            
            if convexity>CIT and new_area<A_MAX_T:
                #actualizar poligono inicial
                where_sql_cat_max="cat="+str(cat_max_neig_1)
                grass.run_command("v.db.update",map='out_poly_1',col='new_set',value=aux_new_set,where=where_sql_cat_max)
                
                #asignar valor de new_set en area maxima
                where_sql_cat_max="cat="+str(cat_max_neig_1)
                grass.run_command("v.db.update",map='polygons_temp',column='new_set',value=aux_new_set, where=where_sql_cat_max)
                grass.run_command("v.dissolve",input='polygons_temp',output='polygons_temp_1',column='new_set',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_1')
                grass.run_command("v.db.addcol",map='polygons_temp_1',col='area double')
                grass.run_command("v.to.db",map='polygons_temp_1',col='area',option='area')
                grass.run_command("v.db.addcol",map='polygons_temp_1',col='new_set int')
                grass.run_command("v.db.update",map='polygons_temp_1',column='new_set',value='cat')
                grass.run_command("g.copy", vect='polygons_temp_1,polygons_temp_2', overwrite=True)
                
                #find neigbords polygons to boundaries in layer 2
                grass.run_command("v.category",input='polygons_temp_2',out='polygons_temp_3',layer='2',type='boundary',option='add',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_3',layer='2',col='left integer,right integer')
                grass.run_command("v.to.db", map='polygons_temp_3',option='sides',col='left,right',layer='2')
                #extract list with area value
                
                #extract list with area value
                area_list=grass.read_command("v.db.select",map='polygons_temp_3',col='area',flags='c')
                area_list1=area_list.rsplit()
                area_list2 = map(float, area_list1)
            
                min1=min(area_list2)
                print "minimo " + str(min1)
                max1=max(area_list2)
                print "maximo " + str(max1)
                
                #category list
                cat_list=grass.read_command("v.db.select",map='polygons_temp_3',col='cat',flags='c')
                cat_list1=cat_list.rsplit()
                cat_list2 = map(int, cat_list1)
                
                grass.run_command("g.remove", vect='polygons_temp',flags='f')
                grass.run_command("db.droptable",table='polygons_temp_1',flags='f')
                grass.run_command("g.copy", vect='polygons_temp_3,polygons_temp', overwrite=True)
            
            
            if convexity<=CIT or new_area>=A_MAX_T:
                print "convexidad no cumple"
                where_sql_cat_max="cat="+str(aux_new_set)
                grass.run_command("v.extract",input='polygons_temp',output='polygons_temp_4',where=where_sql_cat_max,flags='r',overwrite=True)
                
                #find neigbords polygons to boundaries in layer 2
                grass.run_command("v.category",input='polygons_temp_4',out='polygons_temp_5',layer='2',type='boundary',option='add',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_5',layer='2',col='left integer,right integer')
                grass.run_command("v.to.db", map='polygons_temp_5',option='sides',col='left,right',layer='2')
                #extract list with area value
                
                #extract list with area value
                area_list=grass.read_command("v.db.select",map='polygons_temp_5',col='area',flags='c')
                area_list1=area_list.rsplit()
                area_list2 = map(float, area_list1)
            
                min1=min(area_list2)
                print "minimo " + str(min1)
                max1=max(area_list2)
                print "maximo " + str(max1)
                
                #category list
                cat_list=grass.read_command("v.db.select",map='polygons_temp_5',col='cat',flags='c')
                cat_list1=cat_list.rsplit()
                cat_list2 = map(int, cat_list1)
                
                grass.run_command("g.remove", vect='polygons_temp',flags='f')
                grass.run_command("g.copy", vect='polygons_temp_5,polygons_temp', overwrite=True)
                
                #actualizar nuevo new_set_aux
                aux_new_set=cat_list2[area_list2.index(max1)]
        
        if len(cat_neig)==0:
            print "no me quedan vecinos"
            where_sql_cat_max="cat="+str(aux_new_set)
            grass.run_command("v.extract",input='polygons_temp',output='polygons_temp_4',where=where_sql_cat_max,flags='r',overwrite=True)
                
            #find neigbords polygons to boundaries in layer 2
            grass.run_command("v.category",input='polygons_temp_4',out='polygons_temp_5',layer='2',type='boundary',option='add',overwrite=True)
            grass.run_command("v.db.addtable",map='polygons_temp_5',layer='2',col='left integer,right integer')
            grass.run_command("v.to.db", map='polygons_temp_5',option='sides',col='left,right',layer='2')
            #extract list with area value
                
            #extract list with area value
            area_list=grass.read_command("v.db.select",map='polygons_temp_5',col='area',flags='c')
            area_list1=area_list.rsplit()
            area_list2 = map(float, area_list1)
            
            min1=min(area_list2)
            print "minimo " + str(min1)
            max1=max(area_list2)
            print "maximo " + str(max1)
                
            #category list
            cat_list=grass.read_command("v.db.select",map='polygons_temp_5',col='cat',flags='c')
            cat_list1=cat_list.rsplit()
            cat_list2 = map(int, cat_list1)
                
            grass.run_command("g.remove", vect='polygons_temp',flags='f')
            grass.run_command("g.copy", vect='polygons_temp_5,polygons_temp', overwrite=True)
                
            #actualizar nuevo new_set_aux
            aux_new_set=cat_list2[area_list2.index(max1)]
        
        print "largo de la lista que queda por disolver = "+ str(len(cat_list2))
        length=len(cat_list2)
    #
    #
    #
    #
    #
    ####disolver areas 
    #
    #
    #
    grass.run_command("v.dissolve",input='out_poly_1',output='polygons_temp_6',column='new_set',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp_6')
    grass.run_command("v.db.addcol",map='polygons_temp_6',col='area double')
    grass.run_command("v.to.db",map='polygons_temp_6',col='area',option='area')
    grass.run_command("v.db.addcol",map='polygons_temp_6',col='new_set int')
    grass.run_command("v.db.update",map='polygons_temp_6',column='new_set',value='cat')
    grass.run_command("g.copy", vect='polygons_temp_6,polygons_temp_7', overwrite=True)
                        
    #find neigbords polygons to boundaries in layer 2
    grass.run_command("v.category",input='polygons_temp_7',out='polygons_temp_8',layer='2',type='boundary',option='add',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp_8',layer='2',col='left integer,right integer')
    grass.run_command("v.to.db", map='polygons_temp_8',option='sides',col='left,right',layer='2')
    #extract list with area value
                        

    #######################################################DISUELVE AREAS PEQUENAS


    #AREA MINIMA 

    
    
    
    grass.run_command("g.copy", vect='polygons_temp_8,out_poly_3', overwrite=True)
    
    #add table and calculate areas
    grass.run_command("v.db.addtable",map='polygons_temp_8')
    grass.run_command("v.db.addcol",map='polygons_temp_8',col='area double')
    grass.run_command("v.db.addcol",map='polygons_temp_8',col='peri double')
    grass.run_command("v.db.addcol",map='polygons_temp_8',col='formfactor double')
    grass.run_command("v.to.db",map='polygons_temp_8',col='area',option='area')
    grass.run_command("v.to.db",map='polygons_temp_8',col='peri',option='perimeter')
    grass.run_command("v.db.update",map='polygons_temp_8',col='formfactor',value='16*area/(peri*peri)')
    
    #extract list with area value
    area_list=grass.read_command("v.db.select",map='polygons_temp_8',col='area',flags='c')
    area_list1=area_list.rsplit()
    area_list2 = map(float, area_list1)
                        
    min1=min(area_list2)
    print "minimo " + str(min1)
    max1=max(area_list2)
    print "maximo " + str(max1)
        
    #category list
    cat_list=grass.read_command("v.db.select",map='polygons_temp_8',col='cat',flags='c')
    cat_list1=cat_list.rsplit()
    cat_list2 = map(int, cat_list1)
            
    length=len(cat_list2)
    #iniciar busqueda de maximos vecinos
    #while length > 1 :
    temp=1
    #iniciar auxiliar que disuelve
    aux_new_set=cat_list2[area_list2.index(max1)]
    while length>1:
        print "################### INICIA EL WHILE####################"
        #buscar categoria asociada al area maxima
        cat_max=cat_list2[area_list2.index(max1)]
        print "inicia en cat max : " + str(cat_max)
        #borrar categoria y area del listado de checkeados
        cat_list2.remove(cat_max)
        area_list2.remove(max1)
            
            
        #asignar valor de new_set en area maxima
        where_sql_cat_max="cat="+str(cat_max)
        grass.run_command("v.db.update",map='polygons_temp_8',column='new_set',value=aux_new_set, where=where_sql_cat_max)
            
        #buscar categorias de los vecinos del area maxima
        where_sql_left="right="+str(cat_max)
        neig_left=grass.read_command("v.db.select",map='polygons_temp_8',col='left',flags='c',layer=2,where=where_sql_left)
        neig_left1=map(int, neig_left.rsplit())
        where_sql_right="left="+str(cat_max)
        neig_right=grass.read_command("v.db.select",map='polygons_temp_8',col='right',flags='c',layer=2,where=where_sql_right)
        neig_right1=map(int, neig_right.rsplit())
        neig=neig_left1+neig_right1
        print "vecinos"
        print neig
        #borrar de cat repetidos, con valor de  -1 y aquellos que no han sido chequeados
        x=0
        cat_neig=[]
        #Delete repeted values
        while x<len(neig):
            z=neig[x]
            if cat_neig.count(z)==0 and z!=-1 and cat_list2.count(z)>0 :
                    
                cat_neig.append(z)
            else :
                print "Repeted Value "+ str(z)
            x+=1
        print "categorias sin -1 y repetidos"
        print cat_neig
        #borrar vecinos con areas grandes
        x=0
        cat_neig_a_small=[]
        #Delete repeted values
        while x<len(cat_neig):
            z=cat_neig[x]
            a_min_cat_neig=area_list2[cat_list2.index(z)]
            where_sql_ff="cat="+str(z)
            if cat_neig_a_small.count(z)==0 and a_min_cat_neig<MIN_A_T: 
                cat_neig_a_small.append(z)
            else :
                print "Repeted Value "+ str(z)
            x+=1
        print "categorias sin -1 y repetidos"
        print cat_neig_a_small
                  
        #en caso que lista de vecinos este vacia se para la iteracion
        if len(cat_neig_a_small)>0:
            for f in cat_neig_a_small:
                #actualizar poligono inicial
                where_sql_cat_max="cat="+str(f)
                grass.run_command("v.db.update",map='out_poly_3',col='new_set',value=aux_new_set,where=where_sql_cat_max)
                
                #asignar valor de new_set en area maxima
                where_sql_cat_max="cat="+str(f)
                grass.run_command("v.db.update",map='polygons_temp_8',column='new_set',value=aux_new_set, where=where_sql_cat_max)
                grass.run_command("v.dissolve",input='polygons_temp_8',output='polygons_temp_1',column='new_set',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_1')
                grass.run_command("v.db.addcol",map='polygons_temp_1',col='area double')
                grass.run_command("v.to.db",map='polygons_temp_1',col='area',option='area')
                grass.run_command("v.db.addcol",map='polygons_temp_1',col='new_set int')
                grass.run_command("v.db.update",map='polygons_temp_1',column='new_set',value='cat')
                grass.run_command("g.copy", vect='polygons_temp_1,polygons_temp_2', overwrite=True)
                
                #find neigbords polygons to boundaries in layer 2
                grass.run_command("v.category",input='polygons_temp_2',out='polygons_temp_3',layer='2',type='boundary',option='add',overwrite=True)
                grass.run_command("v.db.addtable",map='polygons_temp_3',layer='2',col='left integer,right integer')
                grass.run_command("v.to.db", map='polygons_temp_3',option='sides',col='left,right',layer='2')
                #extract list with area value
                
                #extract list with area value
                area_list=grass.read_command("v.db.select",map='polygons_temp_3',col='area',flags='c')
                area_list1=area_list.rsplit()
                area_list2 = map(float, area_list1)
            
                min1=min(area_list2)
                print "minimo " + str(min1)
                max1=max(area_list2)
                print "maximo " + str(max1)
                
                #category list
                cat_list=grass.read_command("v.db.select",map='polygons_temp_3',col='cat',flags='c')
                cat_list1=cat_list.rsplit()
                cat_list2 = map(int, cat_list1)
                
                grass.run_command("g.remove", vect='polygons_temp_8',flags='f')
                grass.run_command("db.droptable",table='polygons_temp_1',flags='f')
                grass.run_command("g.copy", vect='polygons_temp_3,polygons_temp_8', overwrite=True)

            
        if len(cat_neig_a_small)==0:
            print "no me quedan vecinos"
            where_sql_cat_max="cat="+str(aux_new_set)
            grass.run_command("v.extract",input='polygons_temp_8',output='polygons_temp_4',where=where_sql_cat_max,flags='r',overwrite=True)
                    
            #find neigbords polygons to boundaries in layer 2
            grass.run_command("v.category",input='polygons_temp_4',out='polygons_temp_5',layer='2',type='boundary',option='add',overwrite=True)
            grass.run_command("v.db.addtable",map='polygons_temp_5',layer='2',col='left integer,right integer')
            grass.run_command("v.to.db", map='polygons_temp_5',option='sides',col='left,right',layer='2')
            #extract list with area value
                    
            #extract list with area value
            area_list=grass.read_command("v.db.select",map='polygons_temp_5',col='area',flags='c')
            area_list1=area_list.rsplit()
            area_list2 = map(float, area_list1)
                
            min1=min(area_list2)
            print "minimo " + str(min1)
            max1=max(area_list2)
            print "maximo " + str(max1)
                    
            #category list
            cat_list=grass.read_command("v.db.select",map='polygons_temp_5',col='cat',flags='c')
            cat_list1=cat_list.rsplit()
            cat_list2 = map(int, cat_list1)
                    
            grass.run_command("g.remove", vect='polygons_temp_8',flags='f')
            grass.run_command("g.copy", vect='polygons_temp_5,polygons_temp_8', overwrite=True)
                    
            #actualizar nuevo new_set_aux
            aux_new_set=cat_list2[area_list2.index(max1)]
            
        print "largo de la lista que queda por disolver = "+ str(len(cat_list2))
        length=len(cat_list2)
    #
    #
    #
    #
    #
    ####disolver areas 
    #
    #
    #
    grass.run_command("v.dissolve",input='out_poly_3',output='polygons_temp_6',column='new_set',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp_6')
    grass.run_command("v.db.addcol",map='polygons_temp_6',col='area double')
    grass.run_command("v.to.db",map='polygons_temp_6',col='area',option='area')
    grass.run_command("v.db.addcol",map='polygons_temp_6',col='new_set int')
    grass.run_command("v.db.update",map='polygons_temp_6',column='new_set',value='cat')
    grass.run_command("g.copy", vect='polygons_temp_6,polygons_temp_7', overwrite=True)
                            
    #find neigbords polygons to boundaries in layer 2
    grass.run_command("v.category",input='polygons_temp_7',out='polygons_temp_8',layer='2',type='boundary',option='add',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp_8',layer='2',col='left integer,right integer')
    grass.run_command("v.to.db", map='polygons_temp_8',option='sides',col='left,right',layer='2')
    #extract list with area value
                            
    #extract list with area value
    area_list=grass.read_command("v.db.select",map='polygons_temp_8',col='area',flags='c')
    area_list1=area_list.rsplit()
    area_list2 = map(float, area_list1)
                        
    min1=min(area_list2)
    print "minimo " + str(min1)
    max1=max(area_list2)
    print "maximo " + str(max1)
    
    ############################################################################################################    
    
    
    
    
    #copy_rule_1='polygons_temp_8,poly_dissolved_'+str(i)
    #grass.run_command("g.copy", vect=copy_rule_1, overwrite=True)
    #exportar e importar para limpieza topologica topologia
    
    grass.run_command("v.db.dropcol",map='polygons_temp_8',column='cat_')
    grass.run_command("v.out.ogr",input='polygons_temp_8',type='area',dsn='folder_diss',flags='ec',overwrite=True)
    
    folder2=directory+"/folder_diss/polygons_temp_8.shp"
    poly_i='poly_dissolved_'+str(i)
    grass.run_command("v.in.ogr",dsn=folder2,output=poly_i,flags='o',overwrite=True)
    
    #deleting temporal folders
    folder2_rm=directory+"/folder_diss"
    if os.path.exists(folder2_rm): 
        shutil.rmtree(folder2_rm)
    

        
    #paste finals polygons
    if t==0:
        copy_rule_2=poly_i+',polygons_total_1'
        grass.run_command("g.copy", vect=copy_rule_2, overwrite=True)
        remove_i='poly_dissolved_'+str(i)
        grass.run_command("g.remove",vect=remove_i)
        t+=1
    if t>0:
        patch='polygons_total_1,'+poly_i
        print "orden de patch " + patch
        grass.run_command("v.patch", input=patch, output='polygons_total_2', overwrite=True)
        print "ejecute patch "
        grass.run_command("g.copy",vect='polygons_total_2,polygons_total_1', overwrite=True)
        remove_i='poly_dissolved_'+str(i)
        grass.run_command("g.remove",vect=remove_i)
        t+=1


##***************************************************************************************
## limpieza



ogr='polygons_total_2'
ogr_out='polygons_total_3'
snap=0.0001
column_map=polygons_columns

#grass.run_command("v.in.ogr", flags='ce', dsn='D:\work\grassdata\data\Chaudanne2010\ReYvan\MergeSaufTBA.shp', output='clean1', min_area='0', snap='0', overwrite=True)
grass.run_command("v.category", input=ogr, output='clean2', type='boundary', option='add', overwrite=True)
grass.run_command("v.extract", flags='t', input='clean2', output='clean3', type='boundary', overwrite=True)
grass.run_command("v.type", input='clean3', output='clean4', type='boundary,line', overwrite=True)
grass.run_command("v.clean", input='clean4', output='clean5', type='line', tool='snap,break,rmdupl', thresh=snap, overwrite=True)
#grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.centroids", input='clean6', output='clean7', overwrite=True)
grass.run_command("v.category", input='clean7', output='clean8', type='boundary', option='del', overwrite=True)
grass.run_command("v.clean", input='clean8', output='clean9', tool='rmarea', thresh='0', overwrite=True)
grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', ids='1-9999', overwrite=True)
#grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', overwrite=True)
######FALTA EXTRAER AREAS > 0 ... TAMBIEN AYUDA EN LA LIMPIEZA, SE PODRIA EVALUAR TAMBIEN EXTRAER Y REIMPORTAR.
grass.run_command("v.build.polylines", input='clean10', output='clean11', cats='multi', overwrite=True)

#To get attributes using auxiliar col b_cat
grass.run_command("v.db.addtable", map='clean11', col='b_cat INTEGER', layer='1', overwrite=True)
grass.run_command("v.distance", _from='clean11', from_type='centroid', from_layer='1', to=column_map, upload='cat',column='b_cat', overwrite=True)

#export and import from ogr
#grass.run_command('v.out.ogr',flags='ce',input='clean11',dsn='clean11.shp',type='area',overwrite=True)
#grass.run_command("v.in.ogr", flags='ce', dsn='clean11.shp',output='clean12', overwrite=True)
grass.run_command('v.db.addcol',map='clean11',columns='c_cat INT')
grass.run_command('v.db.update', map='clean11',column='c_cat',value='b_cat')

grass.run_command("v.reclass", input='clean11', output='clean12', column='c_cat', overwrite=True)
grass.run_command("v.db.droptable", map='clean12', overwrite=True)
#grass.run_command("db.copy", from_table='clean1', to_table=ogr_out, overwrite=True)
#grass.run_command("db.copy", from_table=column_map, to_table=ogr_out, overwrite=True)
#grass.run_command("v.db.connect", map=ogr_out, table=ogr_out, layer='1', overwrite=True)
grass.run_command("db.copy", from_table=column_map, to_table='clean12', overwrite=True)
grass.run_command("v.db.connect", map='clean12', table='clean12', layer='1', overwrite=True)
#extract only features with category > 0
condition="cat>0"
grass.run_command("v.extract",input='clean12',output='clean13',where=condition,overwrite=True)

#exportar e importar para limpieza topologica topologia
grass.run_command("v.db.dropcol",map='clean13',column='cat_')
grass.run_command("v.out.ogr",input='clean13',type='area',dsn='folder_clean',flags='ec',overwrite=True)

folder2=directory+"/folder_clean/clean13.shp"

grass.run_command("v.in.ogr",dsn=folder2,output=ogr_out,flags='o',overwrite=True)

#deleting temporal folders
folder2_rm=directory+"/folder_clean"
if os.path.exists(folder2_rm): 
    shutil.rmtree(folder2_rm)


#exportar e importar para limpieza topologica topologia
grass.run_command("v.db.dropcol",map=ogr_out,column='cat_')
grass.run_command("v.out.ogr",input=ogr_out,type='area',dsn=ogr_out,flags='ec',overwrite=True)


grass.run_command("g.remove",vect='clean1,clean2,clean3,clean4,clean5,clean6,clean7,clean8,clean9,clean10,clean11,clean12,clean13')




##***************************************************************************************
## limpieza








##***************************************************************************************
## disolucion de poligonos con mal factor de forma
    
    
    
    
polygons_2='polygons_total_3'
#polygons_columns=raw_input("Please enter the name of polygon pre Triangle to get columns: ")
#out_polygons=raw_input("Please enter the name of the output polygon : ")
#CIT=raw_input("Please enter the Convexity Index Threshold : ")





#add column to identify new set of polygons
grass.run_command("v.db.addtable",map=polygons_2)
grass.run_command("v.db.dropcol",map=polygons_2,col='new_set')
grass.run_command("v.db.addcol",map=polygons_2,col='new_set int')
grass.run_command("v.db.update",map=polygons_2,col='new_set',value='cat')

#add table and calculate areas
grass.run_command("v.db.addcol",map=polygons_2,col='area double')
grass.run_command("v.db.addcol",map=polygons_2,col='peri double')
grass.run_command("v.db.addcol",map=polygons_2,col='formfactor double')
grass.run_command("v.to.db",map=polygons_2,col='area',option='area')
grass.run_command("v.to.db",map=polygons_2,col='peri',option='perimeter')
grass.run_command("v.db.update",map=polygons_2,col='formfactor',value='16*area/(peri*peri)')


#sort list the categories, without repeted values
where_sql_0="formfactor<"+str(FF_MIN_T)
category=grass.read_command("v.db.select",map=polygons_2,col='id_mesh',flags='c',where=where_sql_0)
cat2=category.rsplit()
cat3=sorted(map(int, cat2))
x=0
list=[]


#Delete repeted values
print cat3
while x<len(cat3):
    z=int(cat3[x])
    if list.count(z)==0:
        list.append(z)
    else :
        print "Repeted Value "+ str(z)
    x+=1
list_sorted=sorted(list)


#extract polygons to start dissolve rule
t=0
for i in list_sorted:
#for i in [2313]:
    where_sql_1="id_mesh="+str(i)
    grass.run_command("v.extract",input=polygons_2,output='polygons_temp_ff_1',where=where_sql_1,overwrite=True)
    grass.run_command("v.category",input='polygons_temp_ff_1',out='polygons_temp_ff_2',layer='2',type='boundary',option='add',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp_ff_2',layer='2',col='left integer,right integer')
    grass.run_command("v.to.db", map='polygons_temp_ff_2',option='sides',col='left,right',layer='2')
    where_sql_2="formfactor<"+str(FF_MIN_T)
    grass.run_command("v.extract",input='polygons_temp_ff_1',output='polygons_temp_ff_3',where=where_sql_2,overwrite=True)
    #sort list the categories, without repeted values
    cat_ff=grass.read_command("v.db.select",map='polygons_temp_ff_3',col='cat',flags='c')
    cat_ff2=cat_ff.rsplit()
    cat_ff3=sorted(map(int, cat_ff2))
    print "revisando id_mesh = "+ str(i)
    print "categorias con ff menor a threshold"
    print cat_ff3
    
    for n in cat_ff3:
        #buscar categorias de los vecinos del area maxima
        where_sql_left="right="+str(n)
        neig_left=grass.read_command("v.db.select",map='polygons_temp_ff_2',col='left',flags='c',layer=2,where=where_sql_left)
        neig_left1=map(int, neig_left.rsplit())
        where_sql_right="left="+str(n)
        neig_right=grass.read_command("v.db.select",map='polygons_temp_ff_2',col='right',flags='c',layer=2,where=where_sql_right)
        neig_right1=map(int, neig_right.rsplit())
        neig=neig_left1+neig_right1
        print "vecinos"
        print neig
        #borrar de cat repetidos, con valor de  -1 y aquellos que no han sido chequeados
        x=0
        cat_neig=[]
        area_neig=[]
        #Delete repeted values
        while x<len(neig):
            z=neig[x]
            if cat_neig.count(z)==0 and z!=-1:
                cat_neig.append(z)
                where_sql_a="cat="+str(z)               
                a_neig=grass.read_command("v.db.select",map='polygons_temp_ff_1',col='area',flags='c',where=where_sql_a)
                a_neig_1=a_neig.rsplit()
                a_neig_2=float(a_neig_1[0])
                area_neig.append(a_neig_2)
            else :
                print "Repeted Value "+ str(z)
            x+=1
        print "categorias sin -1 y repetidos"
        print cat_neig
        print area_neig
        if len(cat_neig)>0:
            max1=max(area_neig)
            cat_max=cat_neig[area_neig.index(max1)]
            #Actualizar
            where_sql_cat_max="cat="+str(n)
            grass.run_command("v.db.update",map=polygons_2,column='new_set',value=cat_max, where=where_sql_cat_max)
            print "se ha actulizado poly con valor maximo " + str(n)

grass.run_command("v.dissolve",input=polygons_2,output='new_set_disolved',column='new_set',overwrite=True)
grass.run_command("v.db.addtable",map='new_set_disolved')
grass.run_command("v.db.addcol",map='new_set_disolved',col='area double')
grass.run_command("v.to.db",map='new_set_disolved',col='area',option='area')

 
 
 
 
 
 
##***************************************************************************************
## limpieza



ogr='new_set_disolved'
ogr_out=polygons_out
snap=0.0001
column_map=polygons_columns

#grass.run_command("v.in.ogr", flags='ce', dsn='D:\work\grassdata\data\Chaudanne2010\ReYvan\MergeSaufTBA.shp', output='clean1', min_area='0', snap='0', overwrite=True)
grass.run_command("v.category", input=ogr, output='clean2', type='boundary', option='add', overwrite=True)
grass.run_command("v.extract", flags='t', input='clean2', output='clean3', type='boundary', overwrite=True)
grass.run_command("v.type", input='clean3', output='clean4', type='boundary,line', overwrite=True)
grass.run_command("v.clean", input='clean4', output='clean5', type='line', tool='snap,break,rmdupl', thresh=snap, overwrite=True)
#grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.centroids", input='clean6', output='clean7', overwrite=True)
grass.run_command("v.category", input='clean7', output='clean8', type='boundary', option='del', overwrite=True)
grass.run_command("v.clean", input='clean8', output='clean9', tool='rmarea', thresh='0', overwrite=True)
grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', ids='1-9999', overwrite=True)
#grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', overwrite=True)
######FALTA EXTRAER AREAS > 0 ... TAMBIEN AYUDA EN LA LIMPIEZA, SE PODRIA EVALUAR TAMBIEN EXTRAER Y REIMPORTAR.
grass.run_command("v.build.polylines", input='clean10', output='clean11', cats='multi', overwrite=True)

#To get attributes using auxiliar col b_cat
grass.run_command("v.db.addtable", map='clean11', col='b_cat INTEGER', layer='1', overwrite=True)
grass.run_command("v.distance", _from='clean11', from_type='centroid', from_layer='1', to=column_map, upload='cat',column='b_cat', overwrite=True)

#export and import from ogr
#grass.run_command('v.out.ogr',flags='ce',input='clean11',dsn='clean11.shp',type='area',overwrite=True)
#grass.run_command("v.in.ogr", flags='ce', dsn='clean11.shp',output='clean12', overwrite=True)
grass.run_command('v.db.addcol',map='clean11',columns='c_cat INT')
grass.run_command('v.db.update', map='clean11',column='c_cat',value='b_cat')

grass.run_command("v.reclass", input='clean11', output='clean12', column='c_cat', overwrite=True)
grass.run_command("v.db.droptable", map='clean12', overwrite=True)
#grass.run_command("db.copy", from_table='clean1', to_table=ogr_out, overwrite=True)
#grass.run_command("db.copy", from_table=column_map, to_table=ogr_out, overwrite=True)
#grass.run_command("v.db.connect", map=ogr_out, table=ogr_out, layer='1', overwrite=True)
grass.run_command("db.copy", from_table=column_map, to_table='clean12', overwrite=True)
grass.run_command("v.db.connect", map='clean12', table='clean12', layer='1', overwrite=True)
#extract only features with category > 0
condition="cat>0"
grass.run_command("v.extract",input='clean12',output='clean13',where=condition,overwrite=True)

#exportar e importar para limpieza topologica topologia
grass.run_command("v.db.dropcol",map='clean13',column='cat_')
grass.run_command("v.out.ogr",input='clean13',type='area',dsn='folder_clean',flags='ec',overwrite=True)

folder2=directory+"/folder_clean/clean13.shp"

grass.run_command("v.in.ogr",dsn=folder2,output=ogr_out,flags='o',overwrite=True)

#deleting temporal folders
folder2_rm=directory+"/folder_clean"
if os.path.exists(folder2_rm): 
    shutil.rmtree(folder2_rm)


#exportar e importar para limpieza topologica topologia
grass.run_command("v.db.dropcol",map=ogr_out,column='cat_')
grass.run_command("v.out.ogr",input=ogr_out,type='area',dsn=ogr_out,flags='ec',overwrite=True)


grass.run_command("g.remove",vect='clean1,clean2,clean3,clean4,clean5,clean6,clean7,clean8,clean9,clean10,clean11,clean12,clean13')



##################################################
category_aux=grass.read_command("v.db.select",map='polygons_total_2',col='cat',flags='c')
if len(category_aux)==0:
    grass.run_command("v.db.dropcol",map='polygons_total_1',column='cat_')
    copy_rule='polygons_total_1,'+polygons_out
    grass.run_command("g.copy", vect=copy_rule, overwrite=True)
    grass.run_command("v.out.ogr",input=polygons_out,type='area',dsn=polygons_out,flags='ec',overwrite=True)



##***************************************************************************************
## limpieza

#grass.run_command("g.remove",vect='convex_test,polygons_temp_3,polygons_temp_4,polygons_temp_5,polygons_temp_6,polygons_temp_7,new_points,polygons_temp_8,new_set_disolved,polygons_temp_ff_1,out_poly_1,polygons_temp_ff_2,out_poly_3,polygons_temp_ff_3,poly_hull,polygons_total_1,polygons_temp,polygons_total_2,polygons_temp_1,polygons_total_3,polygons_temp_2','out_poly_area_1','out_poly_area_1_disolved',flags='f')


 