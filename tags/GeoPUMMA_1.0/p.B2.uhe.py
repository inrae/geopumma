#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B2.uhe.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
# BASED ON  	: uhe.py Paille Y. 01/05/2010
#               
# PURPOSE       : To create UHE 
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

#'''1. fusionner les polygones de 'parcelles viaires' et de 'trottoir' qui ont le meme identifiant'''
#'''1. merge polygons 'road's parcels' and 'sidewalk' which have the same key'''
parcelles_viaires=raw_input("Please enter the name of the layer for 'parcelles_viaires' : ")
trottoir=raw_input("Please enter the name of the layer for 'trottoir' : ")
liste_parcelles=grass.read_command("v.db.select", map=parcelles_viaires, column='cat', layer='1', flags='c')

for i in liste_parcelles.splitlines():
    grass.run_command("v.extract", flags='t', input=parcelles_viaires, output='temp_parc', where="cat=%s"%i, overwrite=True)
    grass.run_command("v.extract", flags='t', input=trottoir, output='temp_trot', where="cat=%s"%i, overwrite=True)
    grass.run_command("v.overlay", flags='t', ainput='temp_parc', binput='temp_trot',output='overlay', operator='or', overwrite=True)
    grass.run_command("v.db.addtable", map='overlay', layer='1', columns='id integer', overwrite=True)
    grass.run_command("v.db.update", map='overlay', column='id', value='1', overwrite=True)
    grass.run_command("v.dissolve", input='overlay', output='temp',column='id', overwrite=True)
    grass.run_command("g.copy", vect='temp,temp1')
    grass.run_command("v.overlay", flags='t', ainput='temp1', binput='temp', output='temp2', operator='or', overwrite=True)
    grass.run_command("g.remove", vect='temp1,temp', overwrite=True)
    grass.run_command("g.rename", vect='temp2,temp1', overwrite=True)
    grass.run_command("g.remove", flags='f', vect='temp_parc,temp_trot,overlay')
    
#'''2. ajouter les parcelles masquees et nettoyage'''
#'''2. adding masked parcels and cleaning'''
grass.run_command("v.overlay", flags='t', ainput='temp1', binput='parcelles_masquees', output='temp2', overwrite=True)
grass.run_command("v.clean", input='temp2', output='temp3', tool='rmarea', thresh='10', overwrite=True)

#'''3. mettre a jour les elements geometriques avec un champs pour les identifier et un champs qui calcule la surface totale de l'UHE'''
#'''3. updating geometrics elements with a field to identify them and a field that calculates the total area of the UHE'''
grass.run_command("v.db.addtable", map='temp3', columns='id_uhe integer,area double precision', overwrite=True)
grass.run_command("v.distance", _from='temp3', from_type='centroid', from_layer='1', to='parcelles', to_type='area', to_layer='1', upload='cat', column='id_uhe', overwrite=True)
grass.run_command("v.to.db", map='temp3', option='area', units='meters', column='area', overwrite=True)
grass.run_command("g.rename", vect='temp3,uhe', overwrite=True)
grass.run_command("g.remove", vect='temp1,temp2', overwrite=True)    