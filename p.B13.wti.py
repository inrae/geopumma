#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.wtri.py
# AUTHOR(S)     : Sanzana P. 2014
#               
# PURPOSE       : To identify and extract wti from all interfaces
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
all_interfaces=raw_input("Please enter the name of the map with all interfaces : ")
wtri_v1=raw_input("Please enter the name of the wtri : ")
columns = grass.read_command("v.info",map=wtri_v1,flags='c',layer='1')
print columns
id=raw_input("Please enter the name of the column ID of each interfaces (id_interf) : ")
out_wti=raw_input("Please enter the name of the output wti : ")

#Identifying the list with values of id interfaces classified as part of wtri
segment_ditch=grass.read_command("v.db.select",map=wtri_v1,col=id,flags='c')
segm2=segment_ditch.rsplit()
segm3=sorted(segm2)
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
condition=" "
for i in list_sorted:
        print "Building polyline with id number = " + str(i)
        if a==0:
                print "creation of wti_temp_v1"
                condition=condition+id+"="+str(i)+" "
                print condition
                a+=1
        else:
                print "creation of wti_temp_v1"
                condition=condition+" OR " + id+"="+str(i)+" "
                print condition
                
                a+=1

print "condicion final"
print condition
grass.run_command("v.extract",input=all_interfaces,output='wti_temp_v1',where=condition,overwrite=True,flags='r')


copy='wti_temp_v1,'+out_wti
grass.run_command("g.copy", vect=copy, overwrite=True)
grass.run_command("v.db.dropcol",map=out_wti,column='cat_')
grass.run_command("v.out.ogr", input=out_wti, layer=1, dsn=out_wti, overwrite=True)
grass.run_command("g.remove",vect='wti_temp_v1,wti_temp_v2')
