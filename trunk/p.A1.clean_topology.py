#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.all_interfaces.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
# BASED ON  	: clean_ogr.py Paille Y. 01/05/2010
#               
# PURPOSE       : cleaning and maintenance of polygons vectors 
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
import sys
import os
import grass.script as grass
directory = os.getcwd()
print directory
import os.path
import shutil
#####Display the mapset content#####
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors

ogr=raw_input("Please enter the name of the ogr : ")
ogr_out=raw_input("Please enter the name for the ogr clean : ")
snap=raw_input("Please enter the snap threshold snapping (0.1 m recommended): ")
column_map=raw_input("Please enter the map to get the initial columns: ")
    
#exporting polygons into boundaries polylines and cleaning with snap threshold 
grass.run_command("v.category", input=ogr, output='clean2', type='boundary', option='add', overwrite=True)
grass.run_command("v.extract", flags='t', input='clean2', output='clean3', type='boundary', overwrite=True)
grass.run_command("v.type", input='clean3', output='clean4', type='boundary,line', overwrite=True)
grass.run_command("v.clean", input='clean4', output='clean5', type='line', tool='snap,break,rmdupl', thresh=snap, overwrite=True)
grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.centroids", input='clean6', output='clean7', overwrite=True)
grass.run_command("v.category", input='clean7', output='clean8', type='boundary', option='del', overwrite=True)
grass.run_command("v.clean", input='clean8', output='clean9', tool='rmarea', thresh='0', overwrite=True)
grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', ids='1-9999', overwrite=True)
grass.run_command("v.build.polylines", input='clean10', output='clean11', cats='multi', overwrite=True)
    
#getting attributes using auxiliar col b_cat
grass.run_command("v.db.addtable", map='clean11', col='b_cat INTEGER', layer='1', overwrite=True)
grass.run_command("v.distance", _from='clean11', from_type='centroid', from_layer='1', to=column_map, upload='cat',column='b_cat', overwrite=True)
    
    
grass.run_command('v.db.addcol',map='clean11',columns='c_cat INT')
grass.run_command('v.db.update', map='clean11',column='c_cat',value='b_cat')
grass.run_command("v.reclass", input='clean11', output='clean12', column='c_cat', overwrite=True)
grass.run_command("v.db.droptable", map='clean12', overwrite=True)
grass.run_command("db.copy", from_table=column_map, to_table='clean12', overwrite=True)
grass.run_command("v.db.connect", map='clean12', table='clean12', layer='1', overwrite=True)
    
#extract only features with category > 0
condition="cat>0"
grass.run_command("v.extract",input='clean12',output='clean13',where=condition,overwrite=True)
    
    
#exporting and importing from ogr
grass.run_command("v.db.dropcol",map='clean13',column='cat_')
grass.run_command("v.out.ogr",input='clean13',type='area',dsn='folder_clean',flags='ec',overwrite=True)
    
folder2=directory+"/folder_clean/clean13.shp"
    
grass.run_command("v.in.ogr",dsn=folder2,output=ogr_out,flags='o',overwrite=True)
    
#deleting temporal folders
folder2_rm=directory+"/folder_clean"
if os.path.exists(folder2_rm): 
    shutil.rmtree(folder2_rm)
    
    
#to export final cleaning mesh
grass.run_command("v.db.dropcol",map=ogr_out,column='cat_')
grass.run_command("v.to.db",map=ogr_out,col='area',option='area')
grass.run_command("v.out.ogr",input=ogr_out,type='area',dsn=ogr_out,flags='ec',overwrite=True)
    
#removing temporal files
grass.run_command("g.remove",vect='clean1,clean2,clean3,clean4,clean5,clean6,clean7,clean8,clean9,clean10,clean11,clean12,clean13')








