#!/usr/bin/env python
#Clean Script
#'''
#Created on mai 2010
#@author: paille
#'''
import grass.script as grass

#'''Affiche le contenu du mapset'''
#'''Displaying the mapset content'''
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors


#'''1. choix de la couche 'batiments' '''
#'''1. choice of the layer 'batiments' '''
ogr=raw_input("Please enter the name of the ogr : ")
ogr_out=raw_input("Please entre the name of the ogr_out : ")

#'''2. nettoyage topologique de la couche'''
#'''2. cleaning topology of the layer'''
grass.run_command("v.select", ainput=ogr, binput='uhe', output='clean1', overwrite=True)
grass.run_command("v.db.droptable", flags='f', map='clean1', overwrite=True)
grass.run_command("v.category", input='clean1', output='clean2', type='boundary,centroid,area', option='del', overwrite=True)
grass.run_command("v.category", input='clean2', output='clean3', type='boundary,centroid,area', option='add', overwrite=True)
grass.run_command("v.category", input='clean3', output='clean4', type='boundary', option='del', overwrite=True)


#'''3. mise a jour des parametres geometriques'''
#'''3. updating geometrics parameters'''
grass.run_command("v.db.addtable", map='clean4', col='id_uhe integer,area double precision', overwrite=True)
grass.run_command("v.to.db", map='clean4', option='area', units='meters', columns='area', overwrite=True)
grass.run_command("v.extract", input='clean4', output='clean5', type='area', where="area > 0", overwrite=True)
grass.run_command("v.distance", _from='clean5', from_type='centroid', from_layer='1', to='parcelles', to_type='area', to_layer='1', upload='cat', column='id_uhe', overwrite=True)

grass.run_command("v.dissolve", input='clean5', output=ogr_out, column='id_uhe', overwrite=True)
grass.run_command("v.db.addtable", map=ogr_out, col='id_uhe integer, area double precision', overwrite=True)
grass.run_command("v.db.update", map=ogr_out, layer='1', column='id_uhe', qcolumn='cat', overwrite=True) 
grass.run_command("v.to.db", map=ogr_out, option='area', units='meters', columns='area', overwrite=True)


#'''4. suppression des fichiers temporaires'''
#'''4. erasing temporary files'''
grass.run_command("g.remove", flags='f', vect='clean1,clean2,clean3,clean4,clean5', overwrite=True)
