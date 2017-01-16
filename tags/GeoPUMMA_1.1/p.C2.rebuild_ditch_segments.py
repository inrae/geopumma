#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.C2.rebuild_ditch_segments.py
# AUTHOR(S)     : Sanzana P. 01/12/2014
#               
# PURPOSE       : To rebuild topology and to unify acording a particular field
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
#
import grass.script as grass
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the ditch : ")
polygons_out=raw_input("Please enter the name of the output dissolved ditch : ")
columns = grass.read_command("v.info",map=polygons,flags='c',layer='1')
print columns
id=raw_input("Please enter the name of the column ID : ")
segment_ditch=grass.read_command("v.db.select",map=polygons,col=id,flags='c')
segm2=segment_ditch.rsplit()
segm3=sorted(segm2)
grass.run_command("g.remove", vect='ditch_temp')
a=0
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
            a+=1
        else:
            patch="ditch_temp,"+ditch_segm
            grass.run_command("v.patch", input=patch, output='ditch_complete', overwrite=True, flags='e')
            grass.run_command("g.copy", vect='ditch_complete,ditch_temp', overwrite=True)
            a+=1
            print "This Script rebuild " + str(a) +" polylines. "
            grass.run_command("g.remove",  vect=ditch_segm)
grass.run_command("v.clean", input='ditch_temp', output='ditch_temp_clean', tool='break', overwrite=True)
output_file="ditch_temp_clean,"+polygons_out
grass.run_command("g.copy", vect=output_file, overwrite=True)
grass.run_command("v.db.dropcol",map =polygons_out, col='cat_')
grass.run_command("v.out.ogr", input=polygons_out, type='line', dsn=polygons_out, flags='e')
#To obtein a correct category values you must export and import with v.out.ogr and v.in.ogr, and after that remove again "cat_" 
