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
all_interfaces=raw_input("Please enter the name of the map with all interfaces : ")
river=raw_input("Please enter the name of the river : ")
thresh_segm=raw_input("Please enter the minimum length to segment the river (1 m) : ")
out_river=raw_input("Please enter the name of the output segmented river : ")


#extraer nodos de  malla de interfaces
grass.run_command("v.to.points",input=all_interfaces,output='nodes', flags='n',overwrite=True)
#generar buffer al rededor del rio para seleccionar los nodos que segmentaran el rio
grass.run_command("v.buffer",input=river,output='buffer_out_river',distance='0.01', flags='t',overwrite=True)
#seleccionar los nodos que estan cerca del buffer
grass.run_command("v.select",ainput='nodes',binput='buffer_out_river',output='nodes_inside',operator='intersects',overwrite=True)
#insertar nodos al rio y segmentar todos los tramos
grass.run_command("v.net",input=river,points='nodes_inside',output='estero_segmented',operation='connect',thresh='0.001',overwrite=True,flags='c')
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
grass.run_command("v.extract",input='estero_segmented_cat',output='estero_segmented_cat_length',where="length>0.1",overwrite=True)


#disolver los tramos menos a un limite
grass.run_command("v.clean",input='estero_segmented_cat_length',output='estero_clean',tool='snap',thres=thresh_segm,overwrite=True)
#calcular el nuevo largo despues de disolver
grass.run_command("v.to.db",map='estero_clean',option='length',columns='length')
#selecciona solo los que tienen un largo mayor a 0.1
grass.run_command("v.extract",input='estero_clean',output='estero_segmented_dissolved',where="length>0",overwrite=True)

#exportar e importar para limpieza topologica topologia
output='estero_segmented_dissolved,'+out_river
grass.run_command("g.copy",vect=output,overwrite=True)
#agregar columna con largo para borrar aquellas menores a 0.1
grass.run_command("v.db.addcol",map=out_river,col='id int')
grass.run_command("v.db.update", map=out_river,layer=1,column='id', value='cat')

#exportar rio segmentado
grass.run_command("v.out.ogr",input=out_river,type='line',dsn=out_river,flags='e',overwrite=True)
folder_1=directory+"/estero_segmented_folder/"
if os.path.exists(folder_1): 
    shutil.rmtree(folder_1)
    print "Deleting ... " + folder_1
grass.run_command("v.out.ogr",input=river,type='line',dsn=river,flags='es',overwrite=True)    
grass.run_command("g.remove",vect='buffer_out_river,estero_clean,estero_segmented,estero_segmented_cat,estero_segmented_cat_length,estero_segmented_dissolved,nodes,nodes_inside')