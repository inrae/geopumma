#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B1.sidewalk_street.py
# AUTHOR(S)     : Sanzana P. 01/06/2015
# BASED ON  	: clean_ogr.py Paille Y. 01/05/2010
#               
# PURPOSE       : To create sidewalk and portion of street in front of each lot
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
#####Display the mapset content#####
import grass.script as grass
env = grass.gisenv()
print env
#'''
#Created on mai 2010
#@author: paille
#'''
#'''Affiche le contenu du mapset'''
#'''Display the mapset'''

vectors = grass.read_command("g.list", type='vect')
print vectors

occsol=raw_input("Please enter the name of the file 'cadastre' or 'occupation du sol' : ")

#'''1. extraire les parcelles et la voirie'''
#'''1. extracting parcels and road'''
grass.run_command("v.extract", input=occsol, output='parcelles', layer='1', where="extraction = 'parcelle'",overwrite=True)
grass.run_command("v.extract", input=occsol, output='voirie', layer='1', where="extraction = 'route'",overwrite=True)
grass.run_command("v.dissolve", input='voirie', output='voirie_d', column='extraction', overwrite=True)

#'''2. selectionner les parcelles viaires, les parcelles masquees et toutes les entites qui touchent la voirie'''
#'''2. selecting road's parcels, masked parcels and all of entities that touch the road'''
grass.run_command("v.select", ainput='parcelles', binput='voirie', output='parcelles_viaires', overwrite=True)
grass.run_command("v.overlay", ainput='parcelles', binput='parcelles_viaires', output='parcelles_masquees', operator='not', overwrite=True)

grass.run_command("v.extract", flags='r', input=occsol, output='temp', where="extraction = 'route'", overwrite=True)
grass.run_command("v.select", ainput='temp', binput='voirie', output='elements_viaires', overwrite=True)

#'''3. fusion de la 'voirie_dissolve' avec les 'elements_viaires' pour obtenir, ensuite, 
#    les limites par analyse de voisinage '''
#'''3. merging 'voirie_dissolve' with 'elements_viaires' to obtain, after, 
#    boundaries by neighbour analysis'''
grass.run_command("v.overlay", ainput='elements_viaires', binput='voirie_d', output='temp', operator='or', overwrite=True)
grass.run_command("v.build.polylines", input='temp', output='temp1', cats='multi', overwrite=True)

#'''4. identitification des limites communes et des categories voisines'''
#'''4. indentifying common boundaries and neighbour's categories'''
grass.run_command ("v.category", input='temp1', output='category', layer='2', type='boundary', option='add', overwrite=True)
grass.run_command ("v.db.addtable", map='category', layer='2', columns='left integer, right integer', overwrite=True)
grass.run_command("v.to.db", map='category', option='sides', col='left, right', layer='2', type='boundary', overwrite=True)

#'''5. extraction des limites de parcelles adjacentes a la voirie'''
#'''5. extracting boundaries of the adjacent parcel to the road'''
grass.run_command("v.edit", map='temp', tool='create', overwrite=True)
liste_col=grass.read_command("v.db.select", map='temp1', columns='cat', where="b_extracti = 'route'")
print liste_col
for i in liste_col.splitlines():
    grass.run_command("v.extract", input='category', output='temp2', layer='2', where="left <> -1 AND right = %s"%i ,overwrite=True)
    grass.run_command("v.extract", flags='t', input='category', output='temp3', layer='2', where="left = %s AND right <> -1"%i, overwrite=True)
    grass.run_command("v.patch", input='temp,temp2,temp3', output='temp4', overwrite=True)
    grass.run_command("g.remove", vect='temp,temp2,temp3', overwrite=True)
    grass.run_command("g.rename", vect='temp4,temp', overwrite=True)
grass.run_command("v.category", input='temp', output='extract', type='boundary', overwrite=True)
grass.run_command("v.db.addtable", map='extract', layer='1', overwrite=True)

#'''6. extraction des points situes entre les limites'''
#'''6. extracting points situated between boundaries'''
grass.run_command("v.to.points", flags='nt', input='extract', output='temp2', type='line,boundary', overwrite=True)
grass.run_command("v.clean", input='temp2', output='temp3', type='point', tool='rmdupl', overwrite=True)
grass.run_command("v.category", input='temp3', output='temp4', option='del', type='point', overwrite=True)
grass.run_command("v.category", input='temp4', output='temp5', type='point', overwrite=True)
grass.run_command("v.db.addtable", map='temp5', overwrite=True)
grass.run_command("v.select", ainput='temp5', atype='point', binput='voirie_d', output='temp6', overwrite=True)

#'''7. creer une ligne entre les points extraits et la centerline'''
#'''7. creating a line between extracted points and centerline'''
grass.run_command("v.distance", _from='temp6', from_type='point', to='filvoirie', to_type='line', output='distance', upload='dist', column='cat', overwrite=True)
grass.run_command("v.edit", map='distance', type='point', tool='delete', ids='1-99999', overwrite=True)

#'''8. fusionner la voirie, la centerline de la voirie et les lignes du v.distance pour
#obtenir la couche 'trottoir' '''
#'''8. merging the road, the centerline of the road and lines of v.distance to obtain the layer 'trottoir' '''
grass.run_command("v.category", input='voirie_d', output='temp1', type='boundary', option='add', overwrite=True)
grass.run_command("v.extract", input='temp1', output='temp2', type='boundary', overwrite=True)
grass.run_command("v.type", input='temp2', output='temp3', type='boundary,line', overwrite=True)
grass.run_command("v.patch", input='distance,temp3,filvoirie', output='temp4', overwrite=True)
grass.run_command("v.clean", input='temp4', output='temp5', type='line,point', tool='snap,break,rmdupl,rmline', thresh='0.1', overwrite=True)
grass.run_command("v.type", input='temp5', output='temp6', type='line,boundary', overwrite=True)
grass.run_command("v.centroids", input='temp6', output='temp7', overwrite=True)

#'''8.1. extraction des polygones non voulus de la couche 'trottoir' (la reconstruction de la topologie
#a cree des polygones dans les vides)'''
#'''8.1. extracting unwanted polygons from the layer 'trottoir' (the topology have maked polygons in gaps)'''
grass.run_command("v.overlay", flags='t', ainput='temp7', binput='voirie_d', output='temp8', operator='and', overwrite=True)
grass.run_command("v.category", input='temp8', output='temp9', option='del', type='boundary', overwrite=True)
grass.run_command("v.db.addtable", map='temp9', col='id_uhe integer, area double precision', overwrite=True)
grass.run_command("v.to.db", map='temp9', option='area', units='meters', columns='area', overwrite=True)
grass.run_command("v.extract", flags='r', input='temp9', output='temp10', type='area', where="area = 0", overwrite=True)

#'''8.2. mise a jour de la relation de voisinage entre les polygones de la voirie et les polygones
#parcelles viaires permettant de creer les UHE'''
#'''8.2. updating neighborhood relation between road's polygons and road's parcels polygons to create UHE'''
grass.run_command("v.distance", _from='temp10', from_type='centroid', from_layer='1', to='elements_viaires', to_type='area', to_layer='1', upload='cat', column='id_uhe', overwrite=True)

#'''8.3. reclassement des polygones et fusion des limites communes + calcul de la superficie totale de chaque
#polygone voirie'''
#'''8.3. reclassing polygons and merging common boundaries + calculating total area of each road's polygons'''
grass.run_command("v.dissolve", input='temp10', output='temp11', column='id_uhe', overwrite=True)
grass.run_command("v.db.addtable", map='temp11', col='id_uhe integer, area double precision', overwrite=True)
grass.run_command("v.db.update", map='temp11', layer='1', column='id_uhe', qcolumn='cat', overwrite=True) 
grass.run_command("v.to.db", map='temp11', option='area', units='meters', columns='area', overwrite=True)
grass.run_command("g.rename", vect='temp11,trottoir', overwrite=True)
grass.run_command("g.remove", vect='category,extract,distance,temp,temp1,temp2,temp3,temp4,temp5,temp6,temp7,temp8,temp9,temp10', overwrite=True)

grass.run_command("v.out.ogr", input="trottoir", dsn=trottoir, overwrite=True)