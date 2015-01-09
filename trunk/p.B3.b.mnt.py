#!usr/bin/env python
'''
Created on june 2010
@author: paille
'''
 
import grass.script as grass

'''Affiche le contenu du mapset'''
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
rasters = grass.read_command("g.list", type='rast')
print rasters

vector=raw_input("Please enter the name of the vector : ")
raster=raw_input("Please enter the name of the raster : ")


#grass.run_command("r.in.gdal", flags='o', input='C:\Documents and Settings\paille\Bureau\MNT_Yzeron\mnyzeron5m.asc', output='mntyzeron_5m', overwrite=True)
#grass.run_command("r.in.gdal", flags='o', input='D:\work\MNT_Yzeron\mntyzeron_10m.asc', output='mntyzeron_10m', overwrite=True)
#grass.run_command("r.in.gdal", flags='o', input='D:\work\MNT_Yzeron\mntyzeron25.asc', output='mntyzeron_25m', overwrite=True)
#grass.run_command("g.copy", vect='cadastre@PERMANENT,chaudanne', overwrite=True)
grass.run_command("g.region", vect=vector, res='0.5', overwrite=True)
grass.run_command("v.to.rast", input=vector, output='temp', column='cat', type='area', overwrite=True)
grass.run_command("r.mask", flags='o', input='temp', overwrite=True)
#grass.run_command("g.rename", rast='MASK,rast_mask', overwrite=True)
grass.run_command("v.rast.stats", flags='c', vector=vector, raster=raster, colprefix='n', overwrite=True) 
