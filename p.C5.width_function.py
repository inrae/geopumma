#!/usr/bin/env python
#Line direction
import grass.script as grass
###########################################
##### Sript  width_function.py#############
##### Allow to get the width function######
##### Agosto 2010   #######################
##### Autor: Psanzana######################
###########################################
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
ditch_t=raw_input("Please enter the name of the ditch : ")
outlet_t=raw_input("Please enter the name of the oulet : ")
columns_ditch=grass.read_command("v.info",map=ditch_t,flags='c')
print columns_ditch
river_id=raw_input("Please enter column name of the river id : ")
columns_output=grass.read_command("v.info",map=outlet_t,flags='c')
print columns_output
outlet_id=raw_input("Please enter column name of the output id : ")
outlet_count = grass.read_command("v.db.select",map=outlet_t,col=outlet_id,flags='c')
for i in outlet_count.splitlines():
    river_where=river_id+"="+str(i)
    grass.run_command("v.extract",input=ditch_t,output='ditch',where=river_where,overwrite=True)
    ditch="ditch"
    outlet_where=outlet_id+"="+str(i)
    grass.run_command("v.extract",input=outlet_t,output='outlet',where=outlet_where,overwrite=True)
    outlet="outlet"
    #add start and end coordinates in ditch table
    grass.run_command("v.db.addcol",map=ditch,col='start_E double,start_N double,end_E double,end_N double')
    grass.run_command("v.db.addcol",map=ditch,col='start_E_0 double,start_N_0 double,end_E_0 double,end_N_0 double')
    grass.run_command("v.db.addcol",map=ditch,col='start_E_1 double,start_N_1 double,end_E_1 double,end_N_1 double')
    grass.run_command("v.db.addcol",map=ditch,col='Up_Str double')
    grass.run_command("v.db.addcol",map=ditch,col='Do_Str double')
    grass.run_command("v.to.db",map=ditch,option='start',columns='start_E_0,start_N_0')
    grass.run_command("v.to.db",map=ditch,option='end',columns='end_E_0,end_N_0')
    #the next stpes are necessary to resolve floating numeric problems
    grass.run_command("v.db.update",map=ditch,col='start_E_1', value='start_E_0/10000')
    grass.run_command("v.db.update",map=ditch,col='start_E', value='start_E_1*10000')
    grass.run_command("v.db.update",map=ditch,col='start_N_1', value='start_N_0/10000')
    grass.run_command("v.db.update",map=ditch,col='start_N', value='start_N_1*10000')
    grass.run_command("v.db.update",map=ditch,col='end_E_1', value='end_E_0/10000')
    grass.run_command("v.db.update",map=ditch,col='end_E', value='end_E_1*10000')
    grass.run_command("v.db.update",map=ditch,col='end_N_1', value='end_N_0/10000')
    grass.run_command("v.db.update",map=ditch,col='end_N', value='end_N_1*10000')
    grass.run_command("v.db.dropcol",map=ditch,column='start_E_0')
    grass.run_command("v.db.dropcol",map=ditch,column='start_N_0')
    grass.run_command("v.db.dropcol",map=ditch,column='end_E_0')
    grass.run_command("v.db.dropcol",map=ditch,column='end_N_0')
    grass.run_command("v.db.dropcol",map=ditch,column='start_E_1')
    grass.run_command("v.db.dropcol",map=ditch,column='start_N_1')
    grass.run_command("v.db.dropcol",map=ditch,column='end_E_1')
    grass.run_command("v.db.dropcol",map=ditch,column='end_N_1')
    #extract nodes
    grass.run_command("v.to.points",input=ditch,output='temp_point_1',flags='nt',overwrite=True)
    #clean duplicated nodes
    points = grass.read_command("v.out.ascii",input='temp_point_1',fs=',')
    a=open("points_ascii.txt","w")
    a.write(points)
    a.close()
    grass.run_command("v.in.ascii",input='points_ascii.txt',output='temp_point_2',fs=',',overwrite=True, columns='E double, N double,index int')
    grass.run_command("v.clean",input='temp_point_2',output='temp_point_3',tool='rmdupl',overwrite=True)
    #get only nodes cleaned
    points_cleaned = grass.read_command("v.out.ascii",input='temp_point_3',fs=',')
    b=open("points_cleaned.txt","w")
    b.write(points_cleaned)
    b.close()
    grass.run_command("v.in.ascii",input='points_cleaned.txt',output='temp_point_4',fs=',',overwrite=True,columns='E_0 double, N_0 double,index int')
    grass.run_command("v.db.addcol",map='temp_point_4',col='E_1 double,N_1 double,E double,N double')
    #the next stpes are necessary to resolve floating numeric problems
    grass.run_command("v.db.update",map='temp_point_4',col='N_1', value='N_0/10000')
    grass.run_command("v.db.update",map='temp_point_4',col='N', value='N_1*10000')
    grass.run_command("v.db.update",map='temp_point_4',col='E_1', value='E_0/10000')
    grass.run_command("v.db.update",map='temp_point_4',col='E', value='E_1*10000')
    grass.run_command("v.db.update",map='temp_point_4',col='index')
    #get category number of outlet point
    copy_outlet = outlet + ",outlet_temp"
    grass.run_command("g.copy",vect=copy_outlet,overwrite=True)
    grass.run_command("v.db.droptable",flags='f',map='outlet_temp')
    grass.run_command("v.db.addtable",map='outlet_temp')
    grass.run_command("v.db.addcol",map='outlet_temp',col='cat_out int')
    grass.run_command("v.what.vect",vector='outlet_temp',column='cat_out',qvector='temp_point_4',qcolum='cat',dmax='10')
    out_cat_1 = grass.read_command("v.db.select",map='outlet_temp',flags='c',col='cat_out')
    print "out_cat_1 " + out_cat_1
    #delete space with out information
    out_cat_2 = out_cat_1.rsplit()
    out_cat_3 = out_cat_2[0]
    #add nodes to ditch network
    grass.run_command("v.net",input=ditch,points='temp_point_4',output='ditch_points',operation='connect',thresh='1',overwrite=True)
    #list_index
    list_cat = grass.read_command("v.db.select",map='temp_point_4',col='cat',layer='1',flags='c')
    #calculate distances to outlet from start node and end node each line
    for i in list_cat.splitlines():
        c=open("goto.txt","w")	
        text="1 " + str(i)+" "+str(out_cat_3)
        print "texto de nodo a nodo " 
        print text
        c.write(text)
        c.close()
        grass.run_command("v.net.path",input='ditch_points',out='path_temp',file='goto.txt',overwrite=True)
        grass.run_command("v.db.addcol",map='path_temp',col='length double')
        grass.run_command("v.db.update",map='path_temp',col='length',value='0')
        grass.run_command("v.to.db",map='path_temp',col='length',option='length')
        length_temp_1 = grass.read_command("v.db.select",map='path_temp',flags='c',col='length')
        length_temp_2 = length_temp_1.rsplit()
        length_temp_3 = length_temp_2[0]	
        print "Distancia  " + str(length_temp_3)
        E1=grass.read_command("v.db.select",map='temp_point_4',flags='c',col='E',where="cat=%s"%i)
        E2=E1.rsplit()
        E3=E2[0]
        N1=grass.read_command("v.db.select",map='temp_point_4',flags='c',col='N',where="cat=%s"%i)
        N2=N1.rsplit()
        N3=N2[0]
        condition1="start_E=%s"%E3+" AND "+"start_N=%s"%N3
        print condition1
        grass.run_command("v.db.update",map=ditch,col='Up_Str',value=length_temp_3,where=condition1)
        condition2="end_E=%s"%E3+" AND "+"end_N=%s"%N3
        print condition2
        grass.run_command("v.db.update",map=ditch,col='Do_Str',value=length_temp_3,where=condition2)
grass.run_command("g.remove",vect='outlet,ditch_points,outlet_temp,path_temp,temp_point_1,temp_point_2,temp_point_3,temp_point_4',overwrite=True)







