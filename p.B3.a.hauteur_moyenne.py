#!/usr/bin/env python
#Clean Script
#'''
#Created on mai 2010
#@author: paille
#'''
import grass.script as grass

#'''Affiche le contenu du mapset'''
#'''Display the mapset'''
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
rasters = grass.read_command("g.list", type='rast')
print rasters


#'''1. choix des couches '''
#'''1. choice of layers '''
ogr=raw_input("Please enter the name of the ogr : ")
dem=raw_input("Please enter the name of the DEM : ")

#'''2. calcul de la hauteur moyenne'''
#'''2. calculating the average height'''
grass.run_command("v.rast.stats", flags='c', map=ogr, layer='1', raster=dem, colprefix='mnt', overwrite=True) 
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_number', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_minimum', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_maximum', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_range', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_stddev', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_variance', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_coeff_var', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_first_quartile', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_third_quartile', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_percentile_90', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_median', overwrite=True)
grass.run_command("v.db.dropcolumn.py", map=ogr, layer='1', column='mnt_sum', overwrite=True)
grass.run_command("v.db.renamecolumn", map=ogr, layer='1', column='mnt_average,alt', overwrite=True)


