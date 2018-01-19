#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.B9.a.raster_segmentation.py P. 01/12/2014
#               
# PURPOSE       : To segment polygons in groups with similar raster propierty
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
#
import grass.script as grass
env = grass.gisenv()
print env
rast = grass.read_command("g.list", type='rast')
print rast
slope=raw_input("Please enter the name of the slope raster : ")
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygon map : ")
polygons_out=raw_input("Please enter the name of polygon out : ")
slope_thresh=raw_input("Please enter the maximun std desv slope : ")
columns = grass.read_command("v.info",map=polygons,flags='c',layer='1')
print columns
col_slp=raw_input("Please enter the name of the column with std slope : ")
col_area=raw_input("Please enter the name of the column with area value : ")
area_min=raw_input("Please enter the minimun value area to cut polygons : ")
snake_douglas=raw_input("Please choose smoothing algorithm Snake(0) or Snake&Douglas(1) : ")
#extract the polygons with value out of range, and extract ROADS AND UHE polygons.
condition=col_slp+">"+slope_thresh+ " and " + col_area +" > " + area_min+" and NEW_COD_1 > 2000"
print condition
grass.run_command("v.extract",input=polygons,output='polygons_slope_0',where=condition,overwrite=True)
grass.run_command("v.extract",input='polygons_slope_0',output='polygons_slope',where="NEW_COD_1 = 2513 or NEW_COD_1 = 2502",flags='r', overwrite=True)
grass.run_command("v.extract",input=polygons,output='polygons_complement_0',where=condition,flags='r', overwrite=True)
grass.run_command("v.extract",input='polygons_slope_0',output='polygons_complement_1',where="NEW_COD_1 = 2513 or NEW_COD_1 = 2502", overwrite=True)
grass.run_command("v.overlay",ainput='polygons_complement_0',binput='polygons_complement_1',output='polygons_complement',operator="or",overwrite=True)
polygons_segm=grass.read_command("v.db.select",map='polygons_slope',col='cat',flags='c')
grass.run_command("g.remove", vect="new_temp")
for i in polygons_segm.splitlines():
#for i in [1761]:
    print "WORKING ON POLYGON CAT = " + str(i)
    grass.run_command("g.remove", rast="MASK")
    grass.run_command("v.extract",input='polygons_slope',output='poly_to_segm',where="cat=%s"%i,overwrite=True)
    #find first and secpnd percentil
    grass.run_command("g.region", vect='poly_to_segm', align=slope)
    grass.run_command("v.rast.stats", vector="poly_to_segm", raster=slope, colprefix="slp", flags='ec')
    statistics = grass.read_command("v.db.select",map= "poly_to_segm", col="cat,slp_min,slp_max,slp_first_,slp_third_", fs=" ", flags="c")
    print statistics
    statistics_1=statistics.rsplit()
    print statistics_1
    min=statistics_1[1]
    max=statistics_1[2]
    first=statistics_1[3]
    third=statistics_1[4]
    print " min "+ min +" max "+max+" first "+first +" third "+third
    #Create the file to reclassify 
    f=open("reclassify.txt","w")
    rules= "-9999 thru "+first+ " = "+"1\n"+first+" thru "+third+ " = "+"2\n"+third+" thru 9999"+ " = "+"3\n"
    print rules
    f.write(rules)
    f.close()
    grass.run_command("v.to.rast", input='poly_to_segm', output='poly_to_segm' , use='val', overwrite=True )
    grass.mapcalc("MASK=if(isnull(poly_to_segm),null(),1)")
    #grass.run_command("r.mask", input="poly_to_segm", flags='r')
    grass.run_command("r.reclass", input=slope, output='slope_class', rules="reclassify.txt", overwrite=True)
    grass.run_command("r.to.vect", input='slope_class', output='slope_class', feature='area', overwrite=True, flags='s')
    grass.run_command("v.db.addcol", map='slope_class', col="area double")
    grass.run_command("v.to.db", map='slope_class', col='area', option='area')
    #if apply sorted function of python this line must be deleted
    area_max1 = grass.read_command("v.univar", map='slope_class', col='area')
    area_max2=area_max1.rsplit()
    area_max3=area_max2[21]
    area1="area = "+area_max3
    print area_max3
    grass.run_command("v.extract",input='slope_class',output='slope_class_1',where=area1,overwrite=True, flags='r')
    grass.run_command("v.to.db", map='slope_class_1', col='area', option='area')
    area_max1 = grass.read_command("v.univar", map='slope_class_1', col='area')
    area_max2=area_max1.rsplit()
    area_max3=area_max2[21]
    area1="area = "+area_max3
    print area_max3
    grass.run_command("v.extract",input='slope_class_1',output='slope_class_2',where=area1,overwrite=True, flags='r')
    grass.run_command("v.to.db", map='slope_class_2', col='area', option='area')
    area_max1 = grass.read_command("v.univar", map='slope_class_2', col='area')
    area_max2=area_max1.rsplit()
    area_max3=area_max2[21]
    print area_max3
    print  "tercer area = " + area_max3
    area3=0.999*float(area_max3)
    grass.run_command("v.clean", input='slope_class', output='slope_class_clean', tool='rmarea', thresh=area3, overwrite=True)
    #Delete area outside of  poly_to_segm polygon
    grass.run_command ("v.overlay", ainput='slope_class_clean', binput='poly_to_segm', output='slope_class_clean_1', operator='and', overwrite=True)
    #add category to boundry elements and store the boundaries cat
    grass.run_command("v.category",input='slope_class_clean_1',out='polygons_temp',layer='2',type='boundary',option='add', overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp',table='polygons_temp_2',layer='2')
    grass.run_command("v.db.addcol",map='polygons_temp',col='left integer,right integer',layer='2')
    c = grass.read_command("v.info",map='polygons_temp',flags='c',layer='2')
    grass.run_command("v.to.db", map='polygons_temp',option='sides',col='left,right',layer='2')
    #Do not consider when set of new areas does not have boundaries in commun, thats means do not consider irrelevants areas 
    count_aux=grass.read_command("v.db.select", map='polygons_temp', layer='2', col="left,right", flags='c', fs=' ')
    count_aux1=count_aux.split()
    contador1=count_aux1.count('-1')
    contador2=(len(count_aux1)/2)
    if contador1==contador2:
        grass.run_command("g.copy",vect='poly_to_segm,new_bound_centr_clean', overwrite=True)
    else:
        grass.run_command("v.extract",input='polygons_temp',output='out_boundary',where="left = -1 OR right = -1",flags='r', overwrite=True, layer='2', type='boundary')
        grass.run_command("v.type",input='out_boundary',output='out_boundary_line',type='boundary,line',overwrite=True)
        grass.run_command("v.build.polylines", input='out_boundary_line', out='boundary_line', overwrite=True)
        #get only the external boundaries of the slope_class_clean_1
        grass.run_command("v.extract",input='polygons_temp',output='slope_class_clean_bound',where="left = -1 OR right = -1", overwrite=True, layer='2', type='boundary')
        grass.run_command("v.type",input='slope_class_clean_bound',output='slope_boundary_line',type='boundary,line',overwrite=True)
        #extract nodes and connect with boundary of poly_to_segm file
        grass.run_command("v.to.points",input='boundary_line',output='points',flags='n',overwrite=True)
        points = grass.read_command("v.out.ascii",input='points',fs=',')
        a=open("points_ascii.txt","w")
        a.write(points)
        a.close()
        grass.run_command("v.in.ascii",input='points_ascii.txt',output='points_temp',fs=',',overwrite=True,columns='E double, N double,index int')
        grass.run_command("v.db.addcol",map='points_temp',col='dist double')
        #to extract boundary of poly_to_segm
        grass.run_command("v.category",input='poly_to_segm',output='limit_bound_1',type='boundary',overwrite=True)
        grass.run_command("v.extract",input='limit_bound_1',output='boundary_1',type='boundary',overwrite=True)
        grass.run_command("v.type",input='boundary_1',output='limit_line',type='boundary,line',overwrite=True)
        #to get connection lines
        grass.run_command("v.distance",_from='points_temp',to='slope_boundary_line',upload='dist',col='dist', output='connection_1', overwrite=True)
        #do not consider the points that are not near boundary.
        grass.run_command("v.extract",input='points_temp',output='points_temp_1',where='dist<0.01', overwrite=True)  
        grass.run_command("v.distance",_from='points_temp_1',to='limit_line',upload='dist',col='dist', output='connection_2', overwrite=True)
        #to add connection lines
        grass.run_command("v.db.addtable", map='connection_2')
        grass.run_command("v.patch",input='boundary_line,connection_2',output='new_polygon',overwrite=True)
        grass.run_command("v.clean",input='new_polygon',output='new_polygon_clean',tool='snap,rmdupl,break',thresh='0.1',overwrite=True)
        grass.run_command("v.build.polylines", input='new_polygon_clean', out='boundary_line_complete', overwrite=True)
        if int(snake_douglas)==0:
            grass.run_command("v.generalize", input='boundary_line_complete', output='line_snake', type='line', method='snakes', alpha='1', beta='1', overwrite=True)
        else:
            grass.run_command("v.generalize", input='boundary_line_complete', output='line_snake0', type='line', method='douglas', threshold='25', overwrite=True)
            grass.run_command("v.generalize", input='line_snake0', output='line_snake', type='line', method='snakes', alpha='0.8', beta='0.8', overwrite=True)
        #overlay line_snake with contour line of polygons
        grass.run_command("v.patch",input='limit_line,line_snake',output='segmented_line',overwrite=True)
        grass.run_command("v.clean",input='segmented_line',output='segmented_line_clean',tool='snap,break,rmdupl',thresh='0.1',overwrite=True)
        grass.run_command("v.type",input='segmented_line_clean',output='new_bound',type='line,boundary',overwrite=True)
        grass.run_command("v.centroids",input='new_bound',output='new_bound_centr',overwrite=True)
        grass.run_command("v.clean", input='new_bound_centr', output='new_bound_centr_clean_1', tool='rmarea', thresh='10', overwrite=True)
        #Delete all small areas that are outside polygon
        grass.run_command ("v.overlay", ainput='new_bound_centr_clean_1', binput='poly_to_segm', output='slope_class_clean_1_e', operator='and', overwrite=True)
        #add category to boundry elements and store the boundaries cat*************************************************************
        grass.run_command("v.category",input='slope_class_clean_1_e',out='polygons_temp_e',layer='2',type='boundary',option='add', overwrite=True)
        grass.run_command("v.db.addtable",map='polygons_temp_e',table='polygons_temp_2_e',layer='2')
        grass.run_command("v.db.addcol",map='polygons_temp_e',col='left integer,right integer',layer='2')
        c = grass.read_command("v.info",map='polygons_temp_e',flags='c',layer='2')
        grass.run_command("v.to.db", map='polygons_temp_e',option='sides',col='left,right',layer='2')
        grass.run_command("v.extract",input='polygons_temp_e',output='out_boundary_e',where="left = -1 OR right = -1",flags='r', overwrite=True, layer='2', type='boundary')
        grass.run_command("v.type",input='out_boundary_e',output='out_boundary_line_e',type='boundary,line',overwrite=True)
        grass.run_command("v.build.polylines", input='out_boundary_line_e', out='boundary_line_e', overwrite=True)
        grass.run_command("v.to.points",input='boundary_line_e',output='points_e',flags='n',overwrite=True)
        points_e = grass.read_command("v.out.ascii",input='points_e',fs=',')
        a_e=open("points_ascii_e.txt","w")
        a_e.write(points_e)
        a_e.close()
        grass.run_command("v.in.ascii",input='points_ascii_e.txt',output='points_temp_e',fs=',',overwrite=True,columns='E double, N double,index int')
        grass.run_command("v.db.addcol",map='points_temp_e',col='dist double')
        grass.run_command("v.distance",_from='points_temp_e',to='limit_line',upload='dist',col='dist', output='connection_1_e', overwrite=True)
        #do not consider the points that are not near boundary.
        grass.run_command("v.extract",input='points_temp_e',output='points_temp_1_e',where='dist<0.1', overwrite=True)  
        grass.run_command("v.distance",_from='points_temp_1_e',to='limit_line',upload='dist',col='dist', output='connection_1_e', overwrite=True)   
        grass.run_command("v.patch",input='boundary_line_e,connection_1_e',output='new_polygon_e',overwrite=True)
        grass.run_command("v.build.polylines", input='new_polygon_e', out='boundary_line_complete_e', overwrite=True)
        grass.run_command("v.patch",input='boundary_line_complete_e,limit_line',output='segmented_line_e',overwrite=True)
        grass.run_command("v.clean",input='segmented_line_e',output='segmented_line_clean_e',tool='snap,break,rmdupl',thresh='0.05',overwrite=True)
        grass.run_command("v.type",input='segmented_line_clean_e',output='new_bound_e',type='line,boundary',overwrite=True)
        grass.run_command("v.centroids",input='new_bound_e',output='new_bound_centr_e',overwrite=True)
        grass.run_command("v.clean", input='new_bound_centr_e', output='new_bound_centr_clean', tool='rmarea', thresh='10', overwrite=True)
    #crea archivo new_temp vacio, solo se ejecuta esta orden en caso que no exista
    grass.run_command("v.db.droptable", map='new_bound_centr_clean', flags='f')
    grass.run_command("v.db.addtable", map='new_bound_centr_clean')
    grass.run_command("v.db.addcol", map='new_bound_centr_clean', col='ID int')
    grass.run_command("v.db.update", map='new_bound_centr_clean', col='ID', value=i)
    grass.run_command("g.copy",vect='new_bound_centr_clean,new_temp')
    #almacena el poligono en el temporal
    grass.run_command("v.overlay",ainput='new_temp',binput='new_bound_centr_clean',output='new_polygons',operator="or",overwrite=True)
    grass.run_command("v.db.update",map='new_polygons', col='a_ID', value='b_ID', where='a_ID is null')
    grass.run_command("v.db.dropcol", map='new_polygons', col='a_cat')
    grass.run_command("v.db.dropcol", map='new_polygons', col='b_cat')
    grass.run_command("v.db.dropcol", map='new_polygons', col='b_ID')
    grass.run_command("v.db.renamecol", map='new_polygons', col='a_ID,ID')
    grass.run_command("g.copy",vect='new_polygons,new_temp',overwrite=True)
grass.run_command("v.db.addcol", map='new_polygons', col='area double')
grass.run_command("v.to.db", map='new_polygons', col='area', option='area')
grass.run_command("g.remove", rast="MASK")
grass.run_command("g.region", vect='new_polygons', align='lidar@PERMANENT')
grass.run_command("v.rast.stats", vector='new_polygons', raster='lidar@PERMANENT', colprefix="lid", flags='c')
#Delete unnecessary statitics n, min, max, range, mean, stddev, variance, coeff_var, sum
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_n')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_min')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_max')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_range')
#grass.run_command("v.db.dropcol", map='new_polygons', col='lid_mean')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_stddev')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_varian')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_cf_var')
grass.run_command("v.db.dropcol", map='new_polygons', col='lid_sum')
grass.run_command("g.region", vect='new_polygons', align=slope)
grass.run_command("v.rast.stats", vector='new_polygons', raster=slope, colprefix="slp", flags='c')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_n')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_min')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_max')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_range')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_mean')
#grass.run_command("v.db.dropcol", map='new_polygons', col='slp_stddev')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_varian')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_cf_var')
grass.run_command("v.db.dropcol", map='new_polygons', col='slp_sum')
#Modificar Columnas de Archivo de Entrada
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_NEW_COD_,NEW_COD_1')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_SUBW_ID_,SUBW_ID_2')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_SOIL_ID_,SOIL_ID_3')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_GEOL_ID_,GEOL_ID_4')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_MODULE,MODULE')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_LID_MEAN,LID_MEAN')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_SLP_STDD,SLP_STDD')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_area,area')
grass.run_command("v.db.renamecol", map='polygons_complement', col='a_cat,ID')
grass.run_command("v.db.update",map='polygons_complement', col='NEW_COD_1', value='b_NEW_COD_', where='NEW_COD_1 is null')
grass.run_command("v.db.update",map='polygons_complement', col='SUBW_ID_2', value='b_SUBW_ID_', where='SUBW_ID_2 is null')
grass.run_command("v.db.update",map='polygons_complement', col='SOIL_ID_3', value='b_SOIL_ID_', where='SOIL_ID_3 is null')
grass.run_command("v.db.update",map='polygons_complement', col='GEOL_ID_4', value='b_GEOL_ID_', where='GEOL_ID_4 is null')
grass.run_command("v.db.update",map='polygons_complement', col='area', value='b_area', where='area is null')
grass.run_command("v.db.update",map='polygons_complement', col='ID', value='b_cat', where='ID is null')
grass.run_command("v.db.update",map='polygons_complement', col='LID_MEAN', value='b_LID_MEAN', where='LID_MEAN is null')
grass.run_command("v.db.update",map='polygons_complement', col='SLP_STDD', value='b_SLP_STDD', where='SLP_STDD is null')
grass.run_command("v.db.dropcol", map='polygons_complement', col='a_cat_')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_cat')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_cat_')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_NEW_COD_')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_SUBW_ID_')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_SOIL_ID_')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_GEOL_ID_')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_MODULE')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_LID_MEAN')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_SLP_STDD')
grass.run_command("v.db.dropcol", map='polygons_complement', col='b_area')
#unir archivos new polygons y complement
grass.run_command("v.overlay",ainput='polygons_complement',binput='new_polygons',output='polygons_complete_temp',operator="or",overwrite=True)
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_NEW_COD_,NEW_COD_1')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_SUBW_ID_,SUBW_ID_2')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_SOIL_ID_,SOIL_ID_3')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_GEOL_ID_,GEOL_ID_4')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_MODULE,MODULE')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_LID_MEAN,LID_MEAN')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_SLP_STDD,SLP_STDD')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_area,area')
grass.run_command("v.db.renamecol", map='polygons_complete_temp', col='a_ID,ID')
grass.run_command("v.db.dropcol", map='polygons_complete_temp', col='a_cat')
grass.run_command("v.db.dropcol", map='polygons_complete_temp', col='b_cat')
grass.run_command("v.db.update",map='polygons_complete_temp', col='ID', value='b_ID', where='ID is null')
grass.run_command("v.db.update",map='polygons_complete_temp', col='LID_MEAN', value='b_lid_mean', where='LID_MEAN is null')
grass.run_command("v.db.update",map='polygons_complete_temp', col='SLP_STDD', value='b_slp_stdd', where='SLP_STDD is null')
grass.run_command("v.db.update",map='polygons_complete_temp', col='area', value='b_area', where='area is null')
grass.run_command("v.db.dropcol", map='polygons_complete_temp', col='b_ID')
grass.run_command("v.db.dropcol", map='polygons_complete_temp', col='b_lid_mean')
grass.run_command("v.db.dropcol", map='polygons_complete_temp', col='b_slp_stdd')
grass.run_command("v.db.dropcol", map='polygons_complete_temp', col='b_area')
out_polygon="polygons_complete_temp,"+polygons_out
grass.run_command("g.copy", vect=out_polygon, overwrite=True)
for i in polygons_segm.splitlines():
    N=grass.read_command("v.db.select",map=polygons,col='NEW_COD_1',flags='c',where="cat=%s"%i)
    N1=N.rsplit()
    N2=N1[0]
    grass.run_command("v.db.update",map=polygons_out, col='NEW_COD_1', value=N2, where="ID=%s"%i)
    S=grass.read_command("v.db.select",map=polygons,col='SUBW_ID_2',flags='c',where="cat=%s"%i)
    S1=S.rsplit()
    S2=S1[0]
    grass.run_command("v.db.update",map=polygons_out, col='SUBW_ID_2', value=S2, where="ID=%s"%i)
    SO=grass.read_command("v.db.select",map=polygons,col='SOIL_ID_3',flags='c',where="cat=%s"%i)
    SO1=SO.rsplit()
    SO2=SO1[0]
    grass.run_command("v.db.update",map=polygons_out, col='SOIL_ID_3', value=SO2, where="ID=%s"%i)
    G=grass.read_command("v.db.select",map=polygons,col='GEOL_ID_4',flags='c',where="cat=%s"%i)
    G1=G.rsplit()
    G2=G1[0]
    grass.run_command("v.db.update",map=polygons_out, col='GEOL_ID_4', value=G2, where="ID=%s"%i)
    M=grass.read_command("v.db.select",map=polygons,col='MODULE',flags='c',where="cat=%s"%i)
    M1=M.rsplit()
    M2=M1[0]
    grass.run_command("v.db.update",map=polygons_out, col='MODULE', value=M2, where="ID=%s"%i)
polygons_roads=grass.read_command("v.db.select",map=polygons,col='cat',flags='c', where="NEW_COD_1 = 2513 or NEW_COD_1 = 2502")
for i in polygons_roads.splitlines():
    MOD=grass.read_command("v.db.select",map=polygons,col='MODULE',flags='c',where="cat=%s"%i)
    MOD1=MOD.rsplit()
    MOD2=MOD1[0]
    grass.run_command("v.db.update",map=polygons_out, col='MODULE', value=MOD2, where="ID=%s"%i)
