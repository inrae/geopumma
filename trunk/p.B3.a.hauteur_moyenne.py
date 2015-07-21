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
#'''1.- Elegir la capa '''
ogr=raw_input("Please enter the name of the ogr : ")
rasters = grass.read_command("g.list", type='rast')
print rasters
#'''2.- Elegir el DEM '''
dem=raw_input("Please enter the name of the raster : ")
#'''2.- Elegir el DEM '''
rast_prefix=raw_input("Please enter the name of the colprex : ")


#'''2. calcul de la hauteur moyenne'''
#'''2. calculating the average height'''
grass.run_command("v.rast.stats", flags='c', vector=ogr, layer='1', raster=dem, colprefix='dem', overwrite=True) 
grass.run_command("v.db.dropcol", map=ogr, layer='1', column='dem_n')
grass.run_command("v.db.dropcol", map=ogr, layer='1', column='dem_range')
grass.run_command("v.db.dropcol", map=ogr, layer='1', column='dem_varian')
grass.run_command("v.db.dropcol", map=ogr, layer='1', column='dem_cf_var')
grass.run_command("v.db.dropcol", map=ogr, layer='1', column='dem_sum')


name1="dem_mean,"+rast_prefix+"_ave"
grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name1)


#Rellenar altura de aquellos poligonos con 
polygons=ogr
col_fill=rast_prefix+"_ave"
grass.run_command("g.region",rast=dem)
grass.run_command("v.db.addcol", map=polygons, columns="E double,N double")
grass.run_command("v.to.db", map=polygons, option='coor', col='E, N')
condition=col_fill+" IS NULL"
grass.run_command("v.extract", input=polygons, output='polygons_temp', where=condition, overwrite=True)
list_column=grass.read_command("v.db.select",map='polygons_temp',col='cat',flags='c')
for i in list_column.splitlines():
    coordinates = grass.read_command("v.db.select",map='polygons_temp', where="cat=%s"%i, columns='E,N', flags='c', fs=" ")
    c_1=coordinates.rsplit()
    E=c_1[0]
    N=c_1[1]
    centr=E+","+N
    print "Filling Polygon Cat: "+ str(i)
    print "Coordinates centroid: " + centr
    value=grass.read_command("r.what", input=dem, fs=' ', east_north=centr)
    print value
    v_1=value.rsplit()
    v_3=v_1[2]
    print v_3
    where_sql_1="cat="+str(i)
    grass.run_command("v.db.update",map=polygons,col=col_fill,value=v_3,where=where_sql_1)
    col_value_1=0
    grass.run_command("v.db.update",map=polygons,column='dem_stddev',value=0,where=where_sql_1)
    grass.run_command("v.db.update",map=polygons,column='dem_min',value=v_3,where=where_sql_1)
    grass.run_command("v.db.update",map=polygons,column='dem_max',value=v_3,where=where_sql_1)
    #grass.run_command("v.db.update",map=polygons,column='dem_first_quartile',value=v_3,where="cat=%s"%i)
    #grass.run_command("v.db.update",map=polygons,column='dem_third_quartile',value=v_3,where="cat=%s"%i)
grass.run_command("v.db.dropcol", map=polygons, column='N')
grass.run_command("v.db.dropcol", map=polygons, column='E')
grass.run_command("g.remove", flags='f', vect='polygons_temp', overwrite=True)

#cambiar nombre final
name2="dem_stddev,"+rast_prefix+"_std"
grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name2)
name3="dem_min,"+rast_prefix+"_min"
grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name3)
name4="dem_max,"+rast_prefix+"_max"
grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name4)
#name5="dem_first_quartile,"+rast_prefix+"_1quar"
#grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name5)
#name6="dem_third_quartile,"+rast_prefix+"_3quar"
#grass.run_command("v.db.renamecol", map=ogr, layer='1', column=name6)





