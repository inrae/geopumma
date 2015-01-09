#!/usr/bin/env python
#Clean Scr#!/usr/bin/env python
#Clean Script
#'''
#Created on mai 2010
#@author: paille
#'''
import grass.script as grass

'''Affiche le contenu du mapset'''
'''Display mapset content'''
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
rasters = grass.read_command("g.list", type='rast')
print rasters


'''1. importation du raster representant les zones boisees et conversion en vecteur (facultatif) '''
'''1. import raster of wooded areas and conversion in vector (optionnal)'''
#raster=raw_input("Please enter the name of the raster : ")
#resolution=raw_input("Please enter the resolution of the raster : ")
#grass.run_command("g.region", rast=raster, res=resolution, overwrite=True)
#grass.run_command("r.to.vect", input=raster, output='zones_boisees', feature='area', overwrite=True )

'''Determination du pourcentage de vegetation sur un type d'occupation du sol'''
'''Determination of the percentage of vegetation on a type of land'''

'''2. selection des zones recouvertes par les zones boisees'''
'''2. select wooded areas'''
vector=raw_input("Please enter the name of the vector to analyze: ")
grass.run_command("v.overlay", flags='t', ainput='zones_boisees', binput=vector, output='temp', operator='and', overwrite=True)
grass.run_command("v.db.addtable", map='temp', col='area double precision,b_cat INTEGER', layer='1', overwrite=True)

'''2.1. suppression des zones sans surface'''
'''2.1. erase areas with no values'''
grass.run_command("v.to.db", map='temp', column='area', option='area', overwrite=True)
grass.run_command("v.extract", input='temp', output='temp1', type='area', where='area > 0', overwrite=True)

'''2.2. selection des zones pour etablir un lien entre les tables'''
'''2.2. select areas to link tables'''
grass.run_command("v.select", ainput=vector, binput='temp1', output='temp_select', overwrite=True)

'''2.3. insertion des donnees du type d'occupation du sol afin de calculer le pourcentage de vegetation
et pour etablir une clef'''
'''2.3. insert data of landuse to calculate percentage of vegetation and make a key''' 
grass.run_command("v.distance", _from='temp1', from_type='centroid', from_layer='1', to='temp_select', upload='cat',column='b_cat', overwrite=True)
grass.run_command("v.reclass", input='temp1', output=vector+'_boise', column='b_cat', overwrite=True)
grass.run_command("v.db.droptable", map=vector+'_boise', overwrite=True)
grass.run_command("db.copy", from_table='temp_select', to_table=vector+'_boise', overwrite=True)
grass.run_command("v.db.connect", map=vector+'_boise', table=vector+'_boise', layer='1', overwrite=True)

'''2.4. calcul du pourcentage de vegetation et mise a jour des champs'''
'''2.4. calculating of percentage of vegetion and updating datatable'''
grass.run_command("v.db.addcol", map=vector+'_boise', col='area_boise double precision,p_boise double precision', overwrite=True)
grass.run_command("v.to.db", map=vector+'_boise', column='area_boise', option='area', overwrite=True)
grass.run_command("v.db.update", map=vector+'_boise', column='p_boise', qcolumn='(area_boise * 100) / area', overwrite=True)
grass.run_command("v.db.dropcol", map=vector+'_boise', column='area', overwrite=True)

grass.run_command("g.remove", vect='temp,temp1,temp_select', overwrite=True)
