#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.A2_clean_polyline.py
# AUTHOR(S)     : Sanzana P. 01/12/2014
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

#Declaracion de variables

vectors = grass.read_command("g.list", type='vect')
print vectors

ditch_in=raw_input("Please enter the name of the input ditch : ")
ditch_out=raw_input("Please enter the name of the output ditch : ")


grass.run_command("v.clean",input=ditch_in, type='line', output='ditch_clean_1',tool='snap,rmdangle,prune,rmline,rmsa',thresh='0.01',overwrite=True)
grass.run_command("v.clean",input='ditch_clean_1',type='line',output='ditch_clean_0_01_break',tool='break,snap,rmdangle,prune,rmline,rmsa',thresh='0.01',overwrite=True)

#exportar e importar para limpieza topologica
grass.run_command("v.db.dropcol",map ='ditch_clean_0_01_break', column='cat_')
grass.run_command("v.out.ogr",input='ditch_clean_0_01_break',type='line',dsn='ditch_clean_0_01_break',flags='e',overwrite=True)

folder=directory+"/ditch_clean_0_01_break/ditch_clean_0_01_break.shp"
grass.run_command("v.in.ogr",dsn=folder,output=ditch_out,flags='o',overwrite=True)


