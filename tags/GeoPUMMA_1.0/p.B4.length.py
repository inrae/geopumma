#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B4.length.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
# BASED ON  	: length.py Paille Y. 01/05/2010
#               
# PURPOSE       : To calculate length of each UHE to drainage system
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

#'''1. calcul de la longueur pour les UHE (issus de parcelles viaires)'''
#'''1. calculating the length for UHE ( from road's parcels)'''
grass.run_command("v.select", ainput='uhe', binput='voirie_d', output='uhe_viaires', overwrite=True)
grass.run_command("v.extract", input='uhe_viaires', output='temp2', type='centroid', list='1-9999', overwrite=True)
grass.run_command("v.distance", _from='temp2', to='filvoirie', from_type='centroid', to_type='line', output='temp3', upload='dist', column='cat', overwrite=True)
grass.run_command("v.category", input='temp3', output='temp4', type='line', layer='1', overwrite=True)
grass.run_command("v.db.addtable", map='temp4', columns='id_uhe integer,length1 double precision,length double precision', overwrite=True)
grass.run_command("v.to.db", map='temp4', option='length', column='length1', overwrite=True)
grass.run_command("v.db.update", map='temp4', column='length', qcolumn='length1 * 2', overwrite=True)
grass.run_command("v.db.dropcol", map='temp4', column='length1', overwrite=True)
grass.run_command("v.to.points", flags='n', input='temp4', output='temp5', overwrite=True) 
grass.run_command("v.select", ainput='temp5', binput='temp2', output='temp6', overwrite=True)

#'''2. calcul de la longueur pour les parcelles masquees'''
#'''2. calculating the length for masked parcels'''
grass.run_command("v.extract", input='parcelles_masquees', output='temp7', type='centroid', list='1-9999', overwrite=True)
grass.run_command("v.distance", _from='temp7', to='cadastre', from_type='centroid', to_type='boundary', output='length_temp4', upload='dist', column='cat', overwrite=True)
grass.run_command("v.category", input='length_temp4', output='temp8', type='line', layer='1', overwrite=True)
grass.run_command("v.db.addtable", map='temp8', columns='id_uhe integer,length1 double precision,length double precision', overwrite=True)
grass.run_command("v.to.db", map='temp8', option='length', column='length1', overwrite=True)
grass.run_command("v.db.update", map='temp8', column='length', qcolumn='length1 * 2', overwrite=True)
grass.run_command("v.db.dropcol", map='temp8', column='length1', overwrite=True)
grass.run_command("v.to.points", flags='n', input='temp8', output='temp9', overwrite=True) 
grass.run_command("v.select", ainput='temp9', binput='temp7', output='temp10', overwrite=True)

#'''3. fusion des deux types de parcelles et attribution d'une clef '''
#'''3. merging two types of parcels and allocation of a key'''
grass.run_command("v.patch", flags='e', input='temp6,temp10', output='length', overwrite=True)
grass.run_command("v.distance", _from='length', to='parcelles', from_type='point', to_type='area', upload='cat', column='id_uhe', overwrite=True)
grass.run_command("g.remove", vect='length_temp4,uhe_viaires,temp2,temp3,temp4,temp5,temp6,temp7,temp8,temp9,temp10', overwrite=True)
