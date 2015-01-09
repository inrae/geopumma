#!/usr/bin/env python
#Create new subset of polygon with a Convexity Index Threshold
import grass.script as grass
################################################
##### Sript disolve_convex_criteria.py #########
##### Create new sub set the convex polygons ###
##### January 2011  ############################
##### Autor: Psanzana ##########################
################################################
env = grass.gisenv()
print env
vectors = grass.read_command("g.list", type='vect')
print vectors
polygons=raw_input("Please enter the name of the polygon to disolve : ")
polygons_columns=raw_input("Please enter the name of polygon pre Triangle to get columns: ")
out_polygons=raw_input("Please enter the name of the output polygon : ")
convex_thresh=raw_input("Please enter the threshold of the new polygons : ")
dissolve=raw_input("Dissolve small areas: Yes (1) or Not (0): ")
#add table and calculate areas
grass.run_command("v.db.addtable",map=polygons)
grass.run_command("v.db.addcol",map=polygons,col='area double')
grass.run_command("v.db.addcol",map=polygons,col='peri double')
grass.run_command("v.db.addcol",map=polygons,col='convexity double')
grass.run_command("v.to.db",map=polygons,col='area',option='area')
grass.run_command("v.db.update",map=polygons,col='area',value='area+cat/100000')
grass.run_command("v.to.db",map=polygons,col='peri',option='perimeter')
#sort list the categories, without repeted values
category=grass.read_command("v.db.select",map=polygons,col='cat_',flags='c')
cat2=category.rsplit()
cat3=sorted(cat2)
x=0
list=[]
#Delete repeted values
print cat3
while x<len(cat3):
    z=int(cat3[x])
    if list.count(z)==0:
        list.append(z)
    else :
        print "Repeted Value "+ str(z)
    x+=1
list_sorted=sorted(list)
#add column to identify new set of polygons
grass.run_command("v.db.dropcol",map=polygons,col='new_set')
grass.run_command("v.db.addcol",map=polygons,col='new_set int')
grass.run_command("v.db.update",map=polygons,col='new_set',value='-1')
#extract polygons to start dissolve rule
for i in list_sorted:
    grass.run_command("v.extract",input=polygons,output='out_poly_1',where="cat_=%s"%i,overwrite=True)
    #find neigbords polygons to boundaries in layer 2
    grass.run_command("v.category",input='out_poly_1',out='polygons_temp',layer='2',type='boundary',option='add',overwrite=True)
    grass.run_command("v.db.addtable",map='polygons_temp',layer='2',col='left integer,right integer')
    grass.run_command("v.to.db", map='polygons_temp',option='sides',col='left,right',layer='2')
    #transform str to float
    flo=grass.read_command("v.db.select",map='polygons_temp',col='cat,area',flags='c',fs=' ')
    flo2=flo.rsplit()
    b=0
    list_flo=[]
    while b<len(flo2):
        n=float(flo2[b])
        list_flo.append(n)
        b+=1
    #find max area
    a=0
    list_area=[]
    while a<len(list_flo)/2:
        n=list_flo[2*a+1]
        list_area.append(n)
        a+=1
    area_sorted=sorted(list_area)
    max1=area_sorted[len(area_sorted)-1]
    min1=area_sorted[0]
    #category sorted by area
    c=0
    #variable x represent the new sub sets
    x=1
    #list neigbord of polygons joined
    list_joined=[]
    while area_sorted.count(0)!=len(area_sorted):
        cat_max1=int(list_flo[list_flo.index(max1)-1])
        condition="cat="+str(cat_max1)
        print condition
        #select the polygon with maximun area value
        x_fill=x+i*1000
        grass.run_command("v.db.update",map=polygons,col='new_set',value=x_fill,where=condition)
        grass.run_command("v.db.update",map=polygons,col='convexity',value='1',where=condition)
        #always after use max1 in update must be deleted from list_area
        list_area[list_area.index(max1)]=0
        list_joined.append(cat_max1)
        #extract number of category boundaries
        conc2="left="+str(cat_max1)+" or "+"right="+str(cat_max1)
        print conc2
        neig1=grass.read_command("v.db.select",map='polygons_temp',col='left,right',layer='2',where=conc2,flags='c',fs=' ')
        neig2=neig1.rsplit()
        #extract cat_max1 y transform str to int
        b=0
        list_neig=[]
        while b<len(neig2):
            n=int(neig2[b])
            if n==cat_max1 or n==-1 or list_joined.count(n)!=0:
                print "Not valid boundary. Cat de Max "+str(cat_max1)+" or boundary is outside (-1)"+str(n)
            else:
                list_neig.append(n)
            b+=1
        print list_neig
        #if does not have neigbords do not find other triangles
        while len(list_neig)!=0:
            area_max2=[]
            for w in list_neig:
                area_max=list_flo[list_flo.index(w)+1]
                area_max2.append(area_max)
            area_max2_sorted=sorted(area_max2)
            max2=area_max2_sorted[len(area_max2_sorted)-1]
            cat_max2=int(list_flo[list_flo.index(max2)-1])
            condition2="cat="+str(cat_max2)
            print condition2
            grass.run_command("v.db.update",map=polygons,col='new_set',value=x_fill,where=condition2)
            #Check Convexity
            grass.run_command("v.extract",input=polygons,output='convex_test',where="new_set=%s"%x_fill,overwrite=True)
            grass.run_command("v.dissolve",input='convex_test',output='new_set_disolved',column='new_set',overwrite=True)
            grass.run_command("v.db.addtable",map='new_set_disolved')
            grass.run_command("v.db.addcol",map='new_set_disolved',col='peri double')
            grass.run_command("v.to.db",map='new_set_disolved',col='peri',option='perimeter')
            grass.run_command("g.region",vect=polygons)
            grass.run_command("v.to.points",input='convex_test',output='new_points',overwrite=True,flags='v')
            grass.run_command("v.hull",input='new_points',output='poly_hull',overwrite=True,flags='a')
            grass.run_command("v.db.addtable",map='poly_hull')
            grass.run_command("v.db.addcol",map='poly_hull',col='periH double')
            grass.run_command("v.to.db",map='poly_hull',col='periH',option='perimeter')
            hperi=grass.read_command("v.db.select",map='poly_hull',col='periH',flags='c')
            hperi1=hperi.rsplit()
            hperi2=hperi1[0]
            hperi3=float(hperi2)
            peri=grass.read_command("v.db.select",map='new_set_disolved',col='peri',flags='c')
            peri1=peri.rsplit()
            peri2=peri1[0]
            peri3=float(peri2)
            convexity=hperi3/peri3
            grass.run_command("v.db.update",map=polygons,col='convexity',value=convexity,where=condition2)
            if convexity>float(convex_thresh):
                list_area[list_area.index(max2)]=0
                list_joined.append(cat_max2)
                #add new neigbord
                conc3="left="+str(cat_max2)+" or "+"right="+str(cat_max2)
                print conc3
                new_neig1=grass.read_command("v.db.select",map='polygons_temp',col='left,right',layer='2',where=conc3,flags='c',fs=' ')
                new_neig2=new_neig1.rsplit()
                #extract cat_max2 y transform str to int
                b=0
                while b<len(new_neig2):
                    n=int(new_neig2[b])
                    if n==cat_max2 or n==-1 or list_joined.count(n)!=0 or list_neig.count(n)!=0:
                        print "Not valid boundary. Cat de Max "+str(cat_max2)+" or boundary is outside (-1)"+str(n)
                    else:
                        #add new neigbord
                        list_neig.append(n)
                    b+=1
                #Delete this cat_max2 of the temporal list
                list_neig.remove(cat_max2)
                print "lista final while"
                print list_neig
                print "lista  de polygonos adheridos"
                print list_joined
                print "Convexity value = "+ str(convexity)
            else:
                grass.run_command("v.db.update",map=polygons,col='new_set',value='-1',where=condition2)
                list_neig=[]
        area_sorted=sorted(list_area)
        max1=area_sorted[len(area_sorted)-1]
        print area_sorted.count(0)
        print "TOTAL OF NEW SUBSET POLYGONS = " + str(x)
        x+=1
grass.run_command("v.reclass", input=polygons,output='convexity_reclass',column='new_set',overwrite=True)
grass.run_command("v.db.addtable",map='convexity_reclass')
grass.run_command("v.extract",input='convexity_reclass',output='convexity_dissolved',flags='d',overwrite=True)
grass.run_command("v.db.addcol",map='convexity_dissolved',col='cat_ integer')
grass.run_command("v.db.update",map='convexity_dissolved',col='cat_',value='cat/1000')
grass.run_command("v.db.addcol",map='convexity_dissolved',col='area double')
grass.run_command("v.to.db",map='convexity_dissolved',col='area', option='area')
grass.run_command("v.db.update",map='convexity_dissolved',col='area',value='area+cat/100000')
grass.run_command("v.db.addcol",map='convexity_dissolved',col='cat_2 integer')
grass.run_command("v.db.update",map='convexity_dissolved',col='cat_2',value='cat')
#dissolve small areas with neigbord polyogns, areas less than 0.03 of initial area
if int(dissolve)==1:
    for i in list_sorted:
        grass.run_command("v.extract",input='convexity_dissolved',output='small_areas_1',where="cat_=%s"%i,overwrite=True)
        #find neigbords polygons to boundaries in layer 2
        grass.run_command("v.category",input='small_areas_1',out='polygons_temp',layer='2',type='boundary',option='add',overwrite=True)
        grass.run_command("v.db.addtable",map='polygons_temp',layer='2',col='left integer,right integer')
        grass.run_command("v.to.db", map='polygons_temp',option='sides',col='left,right',layer='2')
        #transform str to float
        flo=grass.read_command("v.db.select",map='small_areas_1',col='cat,area',flags='c',fs=' ')
        flo2=flo.rsplit()
        b=0
        list_flo=[]
        while b<len(flo2):
            n=float(flo2[b])
            list_flo.append(n)
            b+=1
        #find max area
        a=0
        area_tot=0
        list_area=[]
        while a<len(list_flo)/2:
            n=list_flo[2*a+1]
            area_tot+=n
            list_area.append(n)
            a+=1
        area_sorted=sorted(list_area)
        min1=area_sorted[0]
        max1=area_sorted[len(area_sorted)-1]
        #add polygon with lowest area value to neigbord 
        list_joined=[]
        list_max=[]
        while min1<0.03*area_tot:
            cat_min1=int(list_flo[list_flo.index(min1)-1])
            #extract number of category boundaries
            conc2="left="+str(cat_min1)+" or "+"right="+str(cat_min1)
            print conc2
            neig1=grass.read_command("v.db.select",map='polygons_temp',col='left,right',layer='2',where=conc2,flags='c',fs=' ')
            neig2=neig1.rsplit()
            #extract cat_min1 y transform str to int
            b=0
            list_neig=[]
            while b<len(neig2):
                n=int(neig2[b])
                if n==cat_min1 or n==-1 or list_joined.count(n)!=0:
                    print "Not valid boundary. Cat de Min "+str(cat_min1)+" or boundary is outside (-1)"+str(n)
                else:
                    list_neig.append(n)
                b+=1
            print list_neig
            if len(list_neig)==0:
                min1=0.03*area_tot
            else:
                area_temp=[]
                for w in list_neig:
                        area=list_flo[list_flo.index(w)+1]
                        area_temp.append(area)
                area_temp_sorted=sorted(area_temp)
                area_max_temp=area_temp_sorted[len(area_temp_sorted)-1]
                cat_max=int(list_flo[list_flo.index(area_max_temp)-1])
                list_max.append(cat_max)
                condition_cat="cat="+str(cat_min1)
                neig_max=grass.read_command("v.db.update",map='convexity_dissolved',col='cat_2',value=cat_max,where=condition_cat)
                if list_max.count(cat_min1):
                    condition_cat2="cat_2="+str(cat_min1)
                    #list of the categories that change of value
                    cats=grass.read_command("v.db.select", input='convexity_dissolved', col='cat', where=condition_cat2, flags='c')
                    neig_max=grass.read_command("v.db.update",map='convexity_dissolved',col='cat_2',value=cat_max,where=condition_cat2)
                #Check Convexity
                grass.run_command("v.extract",input='convexity_dissolved',output='convex_test',where="cat_2=%s"%cat_max,overwrite=True)
                grass.run_command("v.dissolve",input='convex_test',output='new_set_disolved',column='cat_2',overwrite=True)
                grass.run_command("v.db.addtable",map='new_set_disolved')
                grass.run_command("v.db.addcol",map='new_set_disolved',col='peri double')
                grass.run_command("v.to.db",map='new_set_disolved',col='peri',option='perimeter')
                grass.run_command("g.region",vect=polygons)
                grass.run_command("v.to.points",input='convex_test',output='new_points',overwrite=True,flags='v')
                grass.run_command("v.hull",input='new_points',output='poly_hull',overwrite=True,flags='a')
                grass.run_command("v.db.addtable",map='poly_hull')
                grass.run_command("v.db.addcol",map='poly_hull',col='periH double')
                grass.run_command("v.to.db",map='poly_hull',col='periH',option='perimeter')
                hperi=grass.read_command("v.db.select",map='poly_hull',col='periH',flags='c')
                hperi1=hperi.rsplit()
                hperi2=hperi1[0]
                hperi3=float(hperi2)
                peri=grass.read_command("v.db.select",map='new_set_disolved',col='peri',flags='c')
                peri1=peri.rsplit()
                peri2=peri1[0]
                peri3=float(peri2)
                convexity=hperi3/peri3
                if convexity>float(convex_thresh):
                    #replace this value for the maximun value to not consider again
                    list_area[list_area.index(min1)]=max1
                    list_joined.append(cat_min1)
                    area_sorted=sorted(list_area)
                    min1=area_sorted[0]
                else:
                    condition_cat="cat="+str(cat_min1)
                    neig_max=grass.read_command("v.db.update",map='convexity_dissolved',col='cat_2',value=cat_min1,where=condition_cat)
                    if list_max.count(cat_min1)>0:
                        for i in cats.split():
                            condition_cat2="cat_2="+str(i)
                            neig_max=grass.read_command("v.db.update",map='convexity_dissolved',col='cat',value=cat_min1,where=condition_cat2)
                    list_area[list_area.index(min1)]=max1
                    list_joined.append(cat_min1)
                    area_sorted=sorted(list_area)
                    min1=area_sorted[0]                   
            print "nueva area minima = " + str(min1)
            print "area total = " + str(area_tot)
    #Dissolve small areas with marker cat_2
    grass.run_command("v.reclass", input='convexity_dissolved',output='convexity_reclass',column='cat_2',overwrite=True)
    grass.run_command("v.db.addtable",map='convexity_reclass')
    grass.run_command("v.extract",input='convexity_reclass',output='convexity_dissolved_2',flags='d',overwrite=True)
    grass.run_command("v.db.addcol",map='convexity_dissolved_2',col='cat_ integer')
    grass.run_command("v.db.update",map='convexity_dissolved_2',col='cat_',value='cat/1000')
else:
    grass.run_command("g.copy", vect='convexity_dissolved,convexity_dissolved_2', overwrite=True)
#copy columns
col = grass.read_command("v.info",map=polygons_columns,flags='c',layer='1')
col1=col.replace("|", " ")
col2a=col1.replace("PRECISION", " ")
col2=col2a.replace("CHARACTER", "varchar(80)")
col3=col2.rsplit()
print col3
n=1
while n < len(col3)/2:
#while n < 6:
    column=col3[2*n+1]
    type=col3[2*n].lower()
    addcol=col3[2*n+1]+" "+col3[2*n].lower()
    print "ADDING COLUMN : " + addcol
    grass.run_command("v.db.addcol",map='convexity_dissolved_2',col=addcol)
    new_cats=grass.read_command("v.db.select",map='convexity_dissolved_2',col='cat',flags='c')
    for i in new_cats.splitlines():
        aux=int(int(i)/1000)
        id=grass.read_command("v.db.select",map=polygons_columns,col=column,flags='c',where="cat=%s"%aux)
        id1=id.rsplit()
        id2=id1[0]
        grass.run_command("v.db.update",map='convexity_dissolved_2',col=column,value=id2,where="cat_=%s"%aux)
    n+=1
copy='convexity_dissolved_2,'+out_polygons
grass.run_command("g.copy",vect=copy,overwrite=True)
grass.run_command("v.db.addcol",map=out_polygons,col='area double')
grass.run_command("v.to.db",map=out_polygons,col='area',option='area')
grass.run_command("v.out.ogr",flags='e',input=out_polygons,type='area',dsn=out_polygons) 
