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

vectors = grass.read_command("g.list", type='vect')
print vectors
vect_remove_dup=raw_input("Please enter the name of vector to remove repeted segments : ")
vect_remove_out=raw_input("Please enter the name of output vector : ")

copy_rule=vect_remove_dup+',temp_repeted'
grass.run_command("g.copy",vect=copy_rule,overwrite=True)

cat_count = grass.read_command("v.db.select",map='temp_repeted',col='cat',flags='c')
list_checked=[]
list_checked_repeted=[]
for i in cat_count.splitlines():
        where_sql="cat="+str(i)
        id_polyg = grass.read_command("v.db.select",map='temp_repeted',where=where_sql,col='id_polyg',flags='c')
        id_polyg2=id_polyg.rsplit()
        id_polyg3=id_polyg2[0]
        id_connect=grass.read_command("v.db.select",map='temp_repeted',where=where_sql,col='id_connect',flags='c')
        id_connect2=id_connect.rsplit()
        id_connect3=id_connect2[0]
        aux_index = str(id_polyg3)+str(id_connect3)
        if list_checked.count(aux_index)==0:
            print where_sql +" se ingresa a la lista"
            list_checked.append(aux_index)
        else:
            list_checked_repeted.append(i)
print "list checked"
print list_checked
print "list repeted"
print list_checked_repeted




list_checked_repeted = map(int, list_checked_repeted)
print list_checked_repeted
        
#build all lines
a=0
condition=" "
for i in list_checked_repeted:
        print "Building polyline with id number = " + str(i)
        if a==0:
                print "creation of wti_temp_v1"
                condition=condition+"cat="+str(i)+" "
                print condition
                a+=1
        else:
                print "creation of wti_temp_v1"
                condition=condition+" OR " + "cat="+str(i)+" "
                print condition
                
                a+=1

print "condicion final"
print condition
grass.run_command("v.extract",input='temp_repeted',output=vect_remove_out,where=condition,overwrite=True,flags='r')
grass.run_command("v.extract",input='temp_repeted',output='dup',where=condition,overwrite=True)
        
        
        
        