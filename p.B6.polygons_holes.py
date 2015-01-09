#!/usr/bin/env python
#Cut the polygons with holes
import grass.script as grass
#############################################
##### Sript polygons_holes.py ###############
##### Fin polygons with holes################
##### December 2010  ########################
##### Autor: Psanzana #######################
#############################################
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygon map : ")
polygons_out=raw_input("Please enter the name of polygon out : ")
grass.run_command("v.category",input=polygons,out='polygons_temp',layer='2',type='boundary',option='add')
grass.run_command("v.db.addtable",map='polygons_temp',table='polygons_3',layer='2')
grass.run_command("v.db.addcol",map='polygons_temp',col='left integer,right integer',layer='2')
c = grass.read_command("v.info",map='polygons_temp',flags='c',layer='2')
print c
grass.run_command("v.to.db", map='polygons_temp',option='sides',col='left,right',layer='2')
grass.run_command("v.db.addcol",map='polygons_temp',col='poly_bound integer')
grass.run_command("v.db.update",map='polygons_temp',col='poly_bound',value='0')
d = grass.read_command("v.info",map='polygons_temp',flags='c',layer='1')
print d
polygons_count = grass.read_command("v.db.select",map='polygons_temp',col='cat',flags='c')
a=0
for i in polygons_count.splitlines():
	conc="left="+str(i)+" OR "+"right="+str(i)
	print conc
	table=grass.read_command("v.db.select",map='polygons_temp',col='left,right',layer='2',where=conc,flags='c')
	count_p=table.count('|')
	grass.run_command("v.db.update",map='polygons_temp',col='poly_bound',value=count_p,where="cat=%s"%i)
	if count_p==1:
		a+=1
		print a
print "It was found " + str(a) + " polygons completly inside other polygons "
island=grass.read_command("v.info",map='polygons_temp',flags='t')
island_1=island.rsplit()
island_2=island_1[6]
island_3=island_2.replace("islands=","")
print "It was found " + str(island_3) +" polygons with island inside"
polygons_hole=grass.read_command("v.db.select",map='polygons_temp',col='cat',where='poly_bound=1',flags='c')
print polygons_hole
cadena=""
cadena_ant=""
for i in polygons_hole.splitlines():
	#poligono interior
	out_poly_1="poly"+str(i)
	grass.run_command("v.extract",input='polygons_temp',output=out_poly_1,where="cat=%s"%i,overwrite=True)
	#almacenar los poligonos
	copy_poly=out_poly_1+",poly_inside_temp"
	grass.run_command("g.copy",vect=copy_poly)
	grass.run_command("v.overlay",ainput='poly_inside_temp',binput=out_poly_1,output='polys_inside_final',operator='or',overwrite=True)
	grass.run_command("g.copy",vect='polys_inside_final,poly_inside_temp',overwrite=True)
	#buscar poligono vecino
	conc2="left="+str(i)+" OR "+"right="+str(i)
	print conc2
	neig1=grass.read_command("v.db.select",map='polygons_temp',col='left,right',layer='2',where=conc2,flags='c',fs=' ')
	neig2=neig1.rsplit()
	#selecciona al poligono vecino que puede estar a la derecha o a la izquierda
	if neig2[0]==i:
		neig3=neig2[1]
	else:
		neig3=neig2[0]
	neig4=neig3.replace(" ","")
	neig="neig_"+neig4
	neig5=int(neig4)
	#extract un solo poligono vecino
	grass.run_command("v.extract",input='polygons_temp',output=neig,where="cat=%s"%neig4,overwrite=True)
	out_pol=neig+out_poly_1
	grass.run_command("v.overlay",ainput=neig,binput=out_poly_1,output=out_pol,operator='or',overwrite=True)
	grass.run_command("v.buffer",input=out_pol,output='limit',buffer='0',overwrite=True)
	grass.run_command("v.category",input='limit',output='limit_bound',type='boundary',overwrite=True)
	grass.run_command("v.extract",input='limit_bound',output='boundary',type='boundary',overwrite=True)
	grass.run_command("v.type",input='boundary',output='limit_line_out',type='boundary,line',overwrite=True)
	#sacar bordes del poligono interior
	grass.run_command("v.category",input=out_poly_1,output='limit_bound_1',type='boundary',overwrite=True)
	grass.run_command("v.extract",input='limit_bound_1',output='boundary_1',type='boundary',overwrite=True)
	grass.run_command("v.type",input='boundary_1',output='limit_line_inside',type='boundary,line',overwrite=True)
	#transformar bordes en punto
	grass.run_command("v.to.points",input='limit_line_inside',output='points',flags='v',overwrite=True)
	points = grass.read_command("v.out.ascii",input='points',fs=',')
	a=open("points_ascii.txt","w")
	a.write(points)
	a.close()
	grass.run_command("v.in.ascii",input='points_ascii.txt',output='points_temp',fs=',',overwrite=True,columns='E double, N double,index int')
	grass.run_command("v.db.addcol",map='points_temp',col='dist double')
	#calcular distancias
	grass.run_command("v.distance",_from='points_temp',to='limit_line_out',upload='dist',col='dist')
	dist = grass.read_command("v.db.select",map='points_temp',flags='c',col="dist")
	print dist
	max=0
	for i in dist.splitlines():
		if float(i)>max:
			max=float(i)
	min=max
	for i in dist.splitlines():
		if float(i)<min:
			min=float(i)
	#crear lineas con distancia minima y maxima
	extract="dist="+str(max)+" OR "+"dist="+str(min)
	print extract
	grass.run_command("v.extract",input='points_temp',output='points_max_min',where=extract,overwrite=True)
	grass.run_command("v.distance",_from='points_max_min',to='limit_line_out',output='cut_lines',upload='dist',col='dist',overwrite=True)
	grass.run_command("v.clean", input='cut_lines', output='cut_lines_clean',tool='snap,break,rmdupl', thresh='0.1',overwrite=True)
	#unir conjunto de lineas exterior interior y lineas maximas y minimas
	grass.run_command("v.patch",input='cut_lines_clean,limit_line_out,limit_line_inside',output='new_polygon',overwrite=True)
	grass.run_command("v.clean",input='new_polygon',output='new_polygon_clean',tool='snap,rmdupl,break',thresh='0.1',overwrite=True)
	grass.run_command("v.type",input='new_polygon_clean',output='new_bound',type='line,boundary',overwrite=True)
	grass.run_command("v.centroids",input='new_bound',output='new_bound_centr',overwrite=True)
	#crea archivo new_temp vacio, solo se ejecuta esta orden en caso que no exista
	grass.run_command("g.copy",vect='new_bound_centr,new_temp')
	#almacena el poligono en el temporal
	grass.run_command("v.overlay",ainput='new_temp',binput='new_bound_centr',output='new_polygons',operator="or",overwrite=True)
	grass.run_command("g.copy",vect='new_polygons,new_temp',overwrite=True)
	#borrar los poligonos islas a los poligonos particionados
	grass.run_command("v.overlay",ainput='new_polygons',binput='polys_inside_final',output='final_polygons',operator='not',overwrite=True)
	#generar un extract para todos los poligonos vecinos desde el mapa inicial
	if neig4=="":
		print neig4
	else:
		if cadena_ant=="":
			cadena_ant="cat="+neig4
		else:
			cadena="cat="+neig4+" or "+cadena_ant
			cadena_ant=cadena
	#remover archivos viejos
	grass.run_command("g.remove",vect=out_poly_1)
	grass.run_command("g.remove",vect=neig)
	grass.run_command("g.remove",vect=out_pol)
print cadena
grass.run_command("v.extract",input='polygons_temp',output='polygons_to_part',where=cadena,overwrite=True)
grass.run_command("g.remove",vect='boundary,boundary_1,cut_lines,cut_lines_clean,limit,limit_bound,limit_bound_1,limit_line_inside,limit_line_out,new_bound,new_bound_centr,new_polygon,new_polygon_clean,new_polygons,new_temp,points,points_max_min,points_temp,poly_inside_temp,polys_inside_final'
)
grass.run_command("v.db.droptable",map='final_polygons',flags='f')
#agregar tabla al nuevo conjunto de poligonos
grass.run_command("v.db.addtable",map='final_polygons')
grass.run_command("v.db.addcol",map='final_polygons',col="new_cat integer")
grass.run_command("v.distance",_from='final_polygons',to='polygons_to_part',from_type='centroid',to_type='area',upload='cat',column='new_cat')
#crear el archivo final
#borrar el poligono que se insertara con los poligonos particionados
grass.run_command("v.overlay",ainput='polygons_temp',binput='final_polygons',output='polygons_temp2',operator='not',overwrite=True)
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_new_cod_,new_cod_1')
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_subw_id_,subw_id_2')
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_soil_id_,soil_id_3')
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_geol_id_,geol_id_4')
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_SELF_ID,SELF_ID')
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_type_uhe,type_uhe')
grass.run_command("v.db.renamecol",map='polygons_temp2',col='a_poly_bou,poly_bound')
grass.run_command("v.db.dropcol",map='polygons_temp2',col='a_cat')
grass.run_command("v.db.dropcol",map='polygons_temp2',col='b_cat')
grass.run_command("v.db.dropcol",map='polygons_temp2',col='a_new_cat')
grass.run_command("v.db.dropcol",map='polygons_temp2',col='b_new_cat')
#pegar el poligono
grass.run_command("v.overlay",ainput='polygons_temp2',binput='final_polygons',output=polygons_out,operator='or',overwrite=True)
#actualizar los datos con la columna new_cat
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_new_cod_,new_cod_1')
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_subw_id_,subw_id_2')
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_soil_id_,soil_id_3')
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_geol_id_,geol_id_4')
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_SELF_ID,SELF_ID')
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_type_uhe,type_uhe')
#grass.run_command("v.db.renamecol",map=polygons_out,col='a_poly_bou,poly_bound')
#grass.run_command("v.db.renamecol",map=polygons_out,col='b_new_cat,new_cat')
#grass.run_command("v.db.dropcol",map=polygons_out,col='a_cat')
#grass.run_command("v.db.dropcol",map=polygons_out,col='b_cat')
#grass.run_command("v.db.dropcol",map=polygons_out,col='b_poly_bou')
#grass.read_command("v.db.select",map=polygons_out)
#new_cat=grass.read_command("v.db.select",map='final_polygons',flags='c',col='new_cat')
#for i in new_cat.splitlines():
#	new_cod=grass.read_command("v.db.select",map='polygons_to_part',col='new_cod_1',flags='c',where="cat=%s"%i)
#	print "new cod " +new_cod
#	print str(i)
#	new_cod1=new_cod.rsplit()
#	new_cod2=new_cod1[0]
#	grass.run_command("v.db.update",map=polygons_out,col='new_cod_1',value=new_cod2,where="new_cat=%s"%i)
#	subw_id=grass.read_command("v.db.select",map='polygons_to_part',col='subw_id_2',flags='c',where="cat=%s"%i)
#	print "subw_id " +subw_id
#	print str(i)
#	subw_id1=subw_id.rsplit()
#	subw_id2=subw_id1[0]
#	grass.run_command("v.db.update",map=polygons_out,col='subw_id_2',value=subw_id2,where="new_cat=%s"%i)
#	soil_id=grass.read_command("v.db.select",map='polygons_to_part',col='soil_id_3',flags='c',where="cat=%s"%i)
#	print "soil_id " +soil_id
#	print str(i)
#	soil_id1=soil_id.rsplit()
#	soil_id2=soil_id1[0]
#	grass.run_command("v.db.update",map=polygons_out,col='soil_id_3',value=soil_id2,where="new_cat=%s"%i)
#	geol_id=grass.read_command("v.db.select",map='polygons_to_part',col='geol_id_4',flags='c',where="cat=%s"%i)
#	print "geol_id " +geol_id
#	print str(i)
#	geol_id1=geol_id.rsplit()
#	geol_id2=geol_id1[0]
#	grass.run_command("v.db.update",map=polygons_out,col='geol_id_4',value=geol_id2,where="new_cat=%s"%i)
#	SELF_ID=grass.read_command("v.db.select",map='polygons_to_part',col='SELF_ID',flags='c',where="cat=%s"%i)
#	print "SELF_ID " +SELF_ID
#	print str(i)
#	SELF_ID1=SELF_ID.rsplit()
#	SELF_ID2=SELF_ID1[0]
#	grass.run_command("v.db.update",map=polygons_out,col='SELF_ID',value=SELF_ID2,where="new_cat=%s"%i)
#	#type_uhe=grass.read_command("v.db.select",map='polygons_to_part',col='type_uhe',flags='c',where="cat=%s"%i)
#	#print "type_uhe " +type_uhe
#	#print str(i)
#	#type_uhe1=type_uhe.rsplit()
#	#type_uhe2=type_uhe1[0]
#	#grass.run_command("v.db.update",map=polygons_out,col='type_uhe',value=type_uhe2,where="new_cat=%s"%i)
grass.run_command("v.db.dropcol",map=polygons_out,col='poly_bound')
grass.run_command("v.db.dropcol",map=polygons_out,col='new_cat')
#grass.run_command("g.remove",vect='polygons_temp,final_polygons,polygons_to_part')

