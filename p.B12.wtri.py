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

#Declaracion de variables

vectors = grass.read_command("g.list", type='vect')
print vectors
wti_sql=raw_input("Please enter the name of the map with all interfaces : ")
river=raw_input("Please enter the name of the river : ")
out_wtri=raw_input("Please enter the name of the output wtri : ")
min_length=raw_input("Please enter the minimum length to extract the wtri segments: ")


#actulizacion de largos de cada wti
grass.run_command("v.to.db",map=wti_sql,option='length',columns='length')

#generacion del buffer del rio
grass.run_command("v.buffer",input=river,output='buffer_out_river',distance='0.01',flags='t',overwrite=True)

#Extraer WTI al interior del buffer 0.01 m
grass.run_command("v.overlay",ainput=wti_sql,atype='line',binput='buffer_out_river',operator='and',output='wti_select_by_buffer',olayer='0,1,0',overwrite=True)

#agregar columna largo_tmp1, ojo aqui es .py pero en linux debe ser sin .py
grass.run_command("v.db.addcolumn.py",map='wti_select_by_buffer',columns='length_tmp double')

#actualize columns largo, el problema es que una interface puede contener mas de un rio
grass.run_command("v.to.db",map='wti_select_by_buffer',option='length',columns='length_tmp')

#eliminar columnas con valores menor a minimum length y limpiar topologia
where_sql='length_tmp>'+str(min_length)
grass.run_command("v.extract",input='wti_select_by_buffer',where=where_sql,output='wti_deleted_small_length',overwrite=True)
grass.run_command("v.clean",input='wti_deleted_small_length',type='line',output='wti_deleted_small_length_clean',tool='snap,rmdangle,prune,rmline,rmsa',thresh='1.0',overwrite=True)

#cambiar nombre de columna cat_, eliminar si es posible en ubuntu, porque grass windows 7 no deja
grass.run_command("v.db.dropcolumn.py",map='wti_deleted_small_length_clean',column='cat_')

#exportar e importar para limpieza topologica topologia
grass.run_command("v.out.ogr",input='wti_deleted_small_length_clean',type='line',dsn='c:\script',flags='e',overwrite=True)

#v.in.ogr -o --overwrite dsn=C:\script\wti_deleted_small_length.shp
grass.run_command("v.in.ogr",dsn='c:\script\wti_deleted_small_length_clean.shp',flags='o',overwrite=True)

#agregar columna para asignar inicio y final de linea
grass.run_command("v.db.addcolumn",map='wti_deleted_small_length_clean',columns='x double, y double')
grass.run_command("v.to.db",map='wti_deleted_small_length_clean',type='line',option='start',columns='x,y')



#agregar columna river id
grass.run_command("v.db.addcolumn.py",map='wti_deleted_small_length_clean',columns='id_riv double')

#borrar todas las columnas que no son id_riv

#deleting columns
output_river=river+',river'
grass.run_command("g.copy",vect=output_river,overwrite=True)
col = grass.read_command("v.info",map='river',flags='c',layer='1')
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
        column=col3[2*n+1]
        if column!='river_id':
                type=col3[2*n].lower()
                del_col=col3[2*n+1]
                print "DELETING COLUMN : " + del_col
                grass.run_command("v.db.dropcolumn.py",map='river',columns=del_col)
                n+=1
        else:
                n+=1

polygons_count = grass.read_command("v.db.select",map='wti_deleted_small_length_clean',col='cat',flags='c')
for i in polygons_count.splitlines():
#for i in [1]:
        #Rellena el campo id river
        print "WORKING ON POLYGON CAT = " + str(i)
        where_sql= "cat=" + str(i)
        grass.run_command("v.extract",input='wti_deleted_small_length_clean',output='out_poly_1',where=where_sql,overwrite=True)
        E=grass.read_command("v.db.select",map='out_poly_1',col='x',flags='c',where="cat=%s"%i)
        E1=E.rsplit()
        E2=E1[0]
        N=grass.read_command("v.db.select",map='out_poly_1',col='y',flags='c',where="cat=%s"%i)
        N1=N.rsplit()
        N2=N1[0]
        starting=E2+","+N2
        print starting
        id_riv= grass.read_command("v.what", map='river', coordinates=starting, flags='a',distance='0.2')
        id_riv1=id_riv.rsplit()
        print id_riv1
        id_riv2=id_riv1[33]
        print "Category WTRI = " +str(i) + " . river_id = " + str(id_riv2)
        grass.run_command("v.db.update.py",map='wti_deleted_small_length_clean',column='id_riv',value=id_riv2,where="cat=%s"%i)

#cambiar nombre de columna cat_, eliminar si es posible en ubuntu, porque grass windows 7 no deja
grass.run_command("v.db.renamecolumn.py",map='wti_deleted_small_length_clean',column='cat_,cat_temp')
grass.run_command("v.db.dropcolumn.py",map='wti_deleted_small_length_clean',column='altitude')
grass.run_command("v.db.dropcolumn.py",map='wti_deleted_small_length_clean',column='length_tmp')

#crear copias para borde de cada costado a y b
grass.run_command("g.copy",vect='wti_deleted_small_length_clean,wtri_a',overwrite=True)
grass.run_command("g.copy",vect='wti_deleted_small_length_clean,wtri_b',overwrite=True)
#Extraer los que tienen id_a>0, se eliminan bordes sin poligonos
where_sql='id_a>0'
grass.run_command("v.extract",input='wtri_a',where=where_sql,output='wtri_a_1',overwrite=True)
#Disolver con mismo id_a
#grass.run_command("v.build.polylines",input='wtri_a_1',output='wtri_a_2',cats='first',overwrite=True)
output='wtri_a_1,wtri_a_2'
grass.run_command("g.copy",vect=output,overwrite=True)
#Volver a calcular largos
grass.run_command("v.to.db", map='wtri_a_2',option='length',columns='length')
#Extraer los que tienen id_b>0
where_sql='id_b>0'
grass.run_command("v.extract",input='wtri_b',where=where_sql,output='wtri_b_1',overwrite=True)
#Disolver con mismo id_a
#grass.run_command("v.build.polylines",input='wtri_b_1',output='wtri_b_2',cats='first',overwrite=True)
output='wtri_b_1,wtri_b_2'
grass.run_command("g.copy",vect=output,overwrite=True)
#Volver a calcular largos
grass.run_command("v.to.db", map='wtri_b_2',option='length',columns='length')

#renombrar columnas y borrar las repetidas, solo dejar mod_plot,id_plot,center_ge,id_riv
grass.run_command("v.db.renamecolumn.py",map='wtri_a_2',column='mod_a,mod_plot')
grass.run_command("v.db.renamecolumn.py",map='wtri_a_2',column='id_a,id_plot')
grass.run_command("v.db.renamecolumn.py",map='wtri_a_2',column='centera_ge,center_ge')

grass.run_command("v.db.dropcolumn.py",map='wtri_a_2',column='ogc_fid')
grass.run_command("v.db.dropcolumn.py",map='wtri_a_2',column='mod_b')
grass.run_command("v.db.dropcolumn.py",map='wtri_a_2',column='id_b')
grass.run_command("v.db.dropcolumn.py",map='wtri_a_2',column='centerb_ge')
grass.run_command("v.db.dropcolumn.py",map='wtri_a_2',column='x')
grass.run_command("v.db.dropcolumn.py",map='wtri_a_2',column='y')


grass.run_command("v.db.renamecolumn.py",map='wtri_b_2',column='mod_b,mod_plot')
grass.run_command("v.db.renamecolumn.py",map='wtri_b_2',column='id_b,id_plot')
grass.run_command("v.db.renamecolumn.py",map='wtri_b_2',column='centerb_ge,center_ge')

grass.run_command("v.db.dropcolumn.py",map='wtri_b_2',column='ogc_fid')
grass.run_command("v.db.dropcolumn.py",map='wtri_b_2',column='mod_a')
grass.run_command("v.db.dropcolumn.py",map='wtri_b_2',column='id_a')
grass.run_command("v.db.dropcolumn.py",map='wtri_b_2',column='centera_ge')
grass.run_command("v.db.dropcolumn.py",map='wtri_b_2',column='x')
grass.run_command("v.db.dropcolumn.py",map='wtri_b_2',column='y')

#unir bordes wtri del costado a y costado b
#exportar e importar para limpieza topologica topologia
grass.run_command("v.out.ogr",input='wtri_a_2',type='line',dsn='c:\script',flags='e',overwrite=True)

#v.in.ogr -o --overwrite dsn=C:\script\wti_deleted_small_length.shp
grass.run_command("v.in.ogr",dsn='c:\script\wtri_a_2.shp',flags='o',overwrite=True)

#exportar e importar para limpieza topologica topologia
grass.run_command("v.out.ogr",input='wtri_b_2',type='line',dsn='c:\script',flags='e',overwrite=True)

#v.in.ogr -o --overwrite dsn=C:\script\wti_deleted_small_length.shp
grass.run_command("v.in.ogr",dsn='c:\script\wtri_b_2.shp',flags='o',overwrite=True)

grass.run_command("v.patch",input='wtri_a_2,wtri_b_2',output='wtri_all_1',flags='e',overwrite=True)


#genera el mapa de salida
output='wtri_all_1,'+out_wtri
grass.run_command("g.copy",vect=output,overwrite=True)
grass.run_command("g.remove",vect='wti_select_by_buffer,buffer_out_river,wtri_a,wtri_a_1,wtri_a_2,out_poly_1,wtri_b,river,wtri_b_1,wti_deleted_small_length,wtri_b_2,wti_deleted_small_length_clean')

#disolucion de tramos con igual segmento

polygons='wtri_all_1'
polygons_out=out_wtri
#columns = grass.read_command("v.info",map=polygons,flags='c',layer='1')
#print columns
#id=raw_input("Please enter the name of the column ID : ")
id='id_plot'
segment_ditch=grass.read_command("v.db.select",map=polygons,col=id,flags='c')
segm2=segment_ditch.rsplit()
segm3=sorted(segm2)
grass.run_command("g.remove", vect='ditch_temp')
a=0
b=0
n=0
x=0
list=[]
#Delete repeted values
print segm3
while x<len(segm3):
    i=int(segm3[x])
    if list.count(i) ==0:
        list.append(i) 
    else :
        print "Repeted Value "+ str(i)
    x+=1
list_sorted=sorted(list)
print list_sorted
#build all lines 
for i in list_sorted:
        print "Building polyline with id number = " + str(i)
        condition=id+"="+str(i)
        grass.run_command("v.extract",input=polygons,output='ditch_to_build',where=condition,overwrite=True)
        ditch_segm="ditch_"+str(i)
        grass.run_command("v.build.polylines", input='ditch_to_build', output=ditch_segm, overwrite=True, cats='first')
        #check if the first time that we are going to save any information in ditch_temp
        if a==0:
            copy=ditch_segm+",ditch_temp"
            grass.run_command("g.copy", vect=copy, overwrite=True)
            grass.run_command("g.remove",  vect=ditch_segm)
            a+=1
        else:
            patch="ditch_temp,"+ditch_segm
            grass.run_command("v.patch", input=patch, output='ditch_complete', overwrite=True, flags='e')
            grass.run_command("g.copy", vect='ditch_complete,ditch_temp', overwrite=True)
            a+=1
            print "This Script rebuild " + str(a) +" polylines. "
            grass.run_command("g.remove",  vect=ditch_segm)
#grass.run_command("v.clean", input='ditch_temp', output='ditch_temp_clean', tool='break', overwrite=True)
grass.run_command("v.db.dropcolumn",map ='ditch_temp', column='cat_')
grass.run_command("v.out.ogr",input='ditch_temp',type='line',dsn='c:\script',flags='e',overwrite=True)
grass.run_command("v.in.ogr",dsn='c:\script\ditch_temp.shp',flags='o',output='ditch_temp_cat',overwrite=True)
#deleting segments less than threshold
condition="length >"+str(min_length)
grass.run_command("v.extract",input='ditch_temp_cat',output=polygons_out,where=condition,overwrite=True)
grass.run_command("v.db.dropcolumn",map =polygons_out, column='cat_')
#To obtein a correct category values you must export and import with v.out.ogr and v.in.ogr, and after that remove again "cat_"
grass.run_command("g.remove",vect='ditch_complete,ditch_temp,ditch_to_build,wtri_all_1')



