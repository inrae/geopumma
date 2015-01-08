#!/usr/bin/env python
#Clean Script
import grass.script as grass
#####Display the mapset content#####
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors

ogr=raw_input("Please enter the name of the ogr : ")
ogr_out=raw_input("Please enter the name for the ogr clean : ")
snap=raw_input("Please enter the snap threshold snapping (0.1 m recommended): ")
column_map=raw_input("Please enter the map to get the initial columns: ")

#grass.run_command("v.in.ogr", flags='ce', dsn='D:\work\grassdata\data\Chaudanne2010\ReYvan\MergeSaufTBA.shp', output='clean1', min_area='0', snap='0', overwrite=True)
grass.run_command("v.category", input=ogr, output='clean2', type='boundary', option='add', overwrite=True)
grass.run_command("v.extract", flags='t', input='clean2', output='clean3', type='boundary', overwrite=True)
grass.run_command("v.type", input='clean3', output='clean4', type='boundary,line', overwrite=True)
grass.run_command("v.clean", input='clean4', output='clean5', type='line', tool='snap,break,rmdupl', thresh=snap, overwrite=True)
#grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.type", input='clean5', output='clean6', type='line,boundary', overwrite=True)
grass.run_command("v.centroids", input='clean6', output='clean7', overwrite=True)
grass.run_command("v.category", input='clean7', output='clean8', type='boundary', option='del', overwrite=True)
grass.run_command("v.clean", input='clean8', output='clean9', tool='rmarea', thresh='0', overwrite=True)
grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', ids='1-9999', overwrite=True)
#grass.run_command("v.category", input='clean9', output='clean10', option='del', type='boundary', overwrite=True)
######FALTA EXTRAER AREAS > 0 ... TAMBIEN AYUDA EN LA LIMPIEZA, SE PODRIA EVALUAR TAMBIEN EXTRAER Y REIMPORTAR.
grass.run_command("v.build.polylines", input='clean10', output='clean11', cats='multi', overwrite=True)

#To get attributes using auxiliar col b_cat
grass.run_command("v.db.addtable", map='clean11', col='b_cat INTEGER', layer='1', overwrite=True)
grass.run_command("v.distance", _from='clean11', from_type='centroid', from_layer='1', to=column_map, upload='cat',column='b_cat', overwrite=True)

#export and import from ogr
#grass.run_command('v.out.ogr',flags='ce',input='clean11',dsn='clean11.shp',type='area',overwrite=True)
#grass.run_command("v.in.ogr", flags='ce', dsn='clean11.shp',output='clean12', overwrite=True)
grass.run_command('v.db.addcol',map='clean11',columns='c_cat INT')
grass.run_command('v.db.update', map='clean11',column='c_cat',value='b_cat')

grass.run_command("v.reclass", input='clean11', output=ogr_out, column='c_cat', overwrite=True)
grass.run_command("v.db.droptable", map=ogr_out, overwrite=True)
#grass.run_command("db.copy", from_table='clean1', to_table=ogr_out, overwrite=True)
grass.run_command("db.copy", from_table=column_map, to_table=ogr_out, overwrite=True)
grass.run_command("v.db.connect", map=ogr_out, table=ogr_out, layer='1', overwrite=True)

####New version

