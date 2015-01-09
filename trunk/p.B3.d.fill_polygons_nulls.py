#!/usr/bin/env python
#Fill null polygons values
import grass.script as grass
#####Display the mapset content#####
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygons : ")
columns=grass.read_command("v.info", map=polygons, flags='c')
print columns
col_fill=raw_input("Please enter the name of the column that you desire to fill: ")
raster = grass.read_command("g.list", type='rast')
print raster
dem=raw_input("Please enter the name of the dem to fill column values : ")
grass.run_command("g.region",rast=dem)
grass.run_command("v.db.addcolumn.py", map=polygons, column="E double,N double")
grass.run_command("v.to.db", map=polygons, option='coor', col='E, N')
condition=col_fill+" IS NULL"
grass.run_command("v.extract", input=polygons, output='polygons_temp', where=condition, overwrite=True)
list_column=grass.read_command("v.db.select",map='polygons_temp',col='cat',flags='c')
for i in list_column.splitlines():
    coordinates = grass.read_command("v.db.select",map='polygons_temp', where="cat=%s"%i, col='E,N', flags='c', separator=" ")
    c_1=coordinates.rsplit()
    E=c_1[0]
    N=c_1[1]
    centr=E+","+N
    print "Filling Polygon Cat: "+ str(i)
    print "Coordinates centroid: " + centr
    value=grass.read_command("r.what", map=dem, separator=' ', coordinates=centr)
    print value
    v_1=value.rsplit()
    v_3=v_1[2]
    print v_3
    grass.run_command("v.db.update",map=polygons,col=col_fill,value=v_3,where="cat=%s"%i)
grass.run_command("v.db.dropcolumn.py", map=polygons, column='N')
grass.run_command("v.db.dropcolumn.py", map=polygons, column='E')
grass.run_command("g.remove", flags='f', vect='polygons_temp', overwrite=True)



