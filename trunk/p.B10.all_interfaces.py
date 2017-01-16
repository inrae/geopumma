#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.all_interfaces.py
# AUTHOR(S)     : Sanzana P. 02/02/2015
# BASED ON  	: WTIWTRI.py Florent B. 10/01/2011
#               
# PURPOSE       : Identifying and extracting of all interfaces (WTI & WTRI)
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
import shutil
env = grass.gisenv()
print env
import os
directory = os.getcwd()
print directory
import os.path

#printing vectors 
vectors = grass.read_command("g.list", type='vect')
print vectors
landUseStr=raw_input("Please enter the name of the polygon mesh : ")
interfaces_out=raw_input("Please enter the name of the output polygon mesh : ")

#1.Researching for interfaces 
#selecting of driver
grass.run_command("db.connect",driver='sqlite', database='$GISDBASE/$LOCATION_NAME/$MAPSET/sqlite.db')
grass.run_command("db.connect",flags='p')
grass.run_command("db.tables",flags='p')

#getting boundaries of polygon map
grass.run_command("v.db.addcol", map=landUseStr,layer=1,columns='id_mesh int')
grass.run_command("v.db.update", map=landUseStr,layer=1,column='id_mesh', value='cat')
grass.run_command("v.category", input=landUseStr, output='interfaces', layer=2, type='boundary', option='add',  overwrite=True)

#getting neighbours ids of boundaries
grass.run_command("v.db.addtable",  map='interfaces', layer=2,  columns='left integer, right integer')
grass.run_command("v.to.db",  map='interfaces', layer=2,  option='sides', col=['left', 'right'])

#Exporting table to sqlite and reimporting, this step is necesary to apply the module v.db.join
grass.run_command("v.db.dropcol", map='interfaces',layer=1,column='cat_')
print "se ejecuto hasta aqui"

#The location /media/sf_Lyon_2014_psanzana/geopumma/trunk/modules must be changed
folder_module=directory+"/modules"
if os.path.exists(folder_module): 
    shutil.rmtree(folder_module)
    #grass.run_command("db.droptable",flags='f',table='modules_csv')
    print "se borro"
    
print "se ejecuto hasta aca"

grass.run_command("db.out.ogr",input='interfaces', dsn='modules', format='CSV')
#grass.run_command("v.out.ogr", input='interfaces', type='area', layer=1, output='modules', format='CSV',overwrite=True)

dir_module=directory+"/modules/modules.csv"
#dir_module=directory+"/modules/interfaces.csv"
#dir_module=directory+"/modules"
grass.run_command("db.in.ogr",dsn=dir_module)
grass.run_command("db.dropcol",table='modules_csv',column='cat',flags='f')


#linking left cat
#grass.run_command("v.db.join", map='interfaces',column='left', other_table='modules',other_column='id_mesh',layer=2)
grass.run_command("v.db.join", map='interfaces',column='left', otable='modules_csv',ocolumn='id_mesh',layer=2)

grass.run_command("v.db.renamecol", map='interfaces',layer=2, column='module,mod_a')
grass.run_command("v.db.renamecol", map='interfaces',layer=2,column='id_subb_2,subb_a')

#deleting columns

col = grass.read_command("v.info",map='interfaces',flags='c',layer=2)
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
        column=col3[2*n+1]
        if column!="cat" and column!="left" and column!="right" and column!="mod_a" and column!="subb_a":
                type=col3[2*n].lower()
                del_col=col3[2*n+1]
                print "DELETING COLUMN : " + del_col
                grass.run_command("v.db.dropcol",map='interfaces',column=del_col,layer=2)
                n+=1
        else:
                n+=1


#linking  right cat
grass.run_command("v.db.join", map='interfaces',column='right', otable='modules_csv',ocolumn='id_mesh',layer=2)
grass.run_command("v.db.renamecol", map='interfaces',layer=2, column='module,mod_b')
grass.run_command("v.db.renamecol", map='interfaces',layer=2,column='id_subb_2,subb_b')

#deleting columns

col = grass.read_command("v.info",map='interfaces',flags='c',layer=2)
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
        column=col3[2*n+1]
        if column!="cat" and column!="left" and column!="right" and column!="mod_b" and column!="subb_b" and column!="mod_a" and column!="subb_a":
                type=col3[2*n].lower()
                del_col=col3[2*n+1]
                print "DELETING COLUMN : " + del_col
                grass.run_command("v.db.dropcol",map='interfaces',column=del_col,layer=2)
                n+=1
        else:
                n+=1







#export as all interfaces shape


grass.run_command("v.db.renamecol",map='interfaces',column='left,id_mesh_a',layer=2)
grass.run_command("v.db.renamecol",map='interfaces',column='right,id_mesh_b',layer=2)
grass.run_command("v.db.addcol", map='interfaces',layer=2,columns='id_interf int')
grass.run_command("v.db.update", map='interfaces',layer=2,column='id_interf', value='cat')
copy='interfaces,'+interfaces_out
grass.run_command("g.copy", vect=copy, overwrite=True)
grass.run_command("v.out.ogr", input=interfaces_out, type='boundary', layer=2, dsn=interfaces_out, overwrite=True)
grass.run_command("g.remove",vect='interfaces')
grass.run_command("g.remove",vect='modules_csv')
folder_rm_1=directory+"/modules"
if os.path.exists(folder_rm_1): 
    shutil.rmtree(folder_rm_1)
    #grass.run_command("db.droptable",flags='f',table='modules_csv')
    print "se borro"

#selecting dbf driver
grass.run_command("db.connect",driver='dbf', database='$GISDBASE/$LOCATION_NAME/$MAPSET/dbf/')
grass.run_command("db.connect",flags='p')
grass.run_command("db.tables",flags='p')
grass.run_command("v.db.dropcol", map=landUseStr,layer=1,column='cat_')
grass.run_command("v.out.ogr", input=landUseStr, layer=1,type='area', dsn=landUseStr, overwrite=True,flags='c')
grass.run_command("v.in.ogr",dsn=interfaces_out,flags='o',type='line',output=interfaces_out,overwrite=True)


