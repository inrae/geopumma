#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.C3.river_h_s.py
# AUTHOR(S)     : Sanzana P. 01/12/2014
#               
# PURPOSE       : To get altitude and slope of each segment river
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
#Height and slope average
import grass.script as grass
#####Display the mapset content#####
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
ditch=raw_input("Please enter the name of the ditch : ")
raster = grass.read_command("g.list", type='rast')
print raster
dem=raw_input("Please enter the name of the dem : ")
grass.run_command("g.region",rast=dem)
grass.run_command("v.db.addcol", map=ditch, col="meanHeight double")
grass.run_command("v.db.addcol", map=ditch, col="length double")
grass.run_command("v.db.addcol", map=ditch, col="rangetot double")
grass.run_command("v.db.addcol", map=ditch, col="meanSlope double")
grass.run_command("v.to.db", map=ditch, col='length', option='length')
list_ditch = grass.read_command("v.db.select",map=ditch,col='cat',layer='1',flags='c')
for i in list_ditch.splitlines():
    grass.run_command("v.extract",input=ditch,output='temp_ditch',where="cat=%s"%i,overwrite=True)
    grass.run_command("v.to.points",input='temp_ditch',output='temp_point',flags='nt',overwrite=True)
    points = grass.read_command("v.out.ascii",input='temp_point',fs=' ')
    print i	
    #extract coordinates
    points0=points.rsplit()
    c1=points0[0]+','+points0[1]
    c2=points0[3]+','+points0[4]
    #consult height value
    rwhat1=grass.read_command("r.what",input=dem,fs=',',east_north=c1,flags='c')	
    height_erase1=c1+',,'
    height1=rwhat1.replace(height_erase1,'')
    rwhat2=grass.read_command("r.what",input=dem,fs=',',east_north=c2,flags='c')	
    height_erase2=c2+',,'
    height2=rwhat2.replace(height_erase2,'')
    height_average= round(float(height1)/2,2)+ round(float(height2)/2,2)
    grass.run_command("v.db.update", map=ditch, col='meanHeight', where="cat=%s"%i, value=height_average)
    #ramp
    rangetotal= round(float(height1)-float(height2),2)
    grass.run_command("v.db.update", map=ditch, col='rangetot', where="cat=%s"%i, value=rangetotal)
    #slope
    grass.run_command("v.db.update", map=ditch, col='meanSlope', where="cat=%s"%i, value='rangetot/length')
grass.run_command("g.remove", flags='f', vect='temp_point,temp_ditch', overwrite=True)



