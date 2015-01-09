#!/usr/bin/env python
#Create new subset of polygon with a Convexity Index Threshold
'''-------------------- interfOlaf.py ---------------------
   -created by : Florent BROSSARD
   -date : 19/02/2011
---------------------------------------------------------------
'''

#####################################
######### Import libraries  #################
#####################################
##wx (for graphical interfaces)
try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"
##pg (to use postgresql queries)
try:
    import pg
except ImportError:
    raise ImportError,"The pygresql (pg) module is required to run this program"
##copy (for copiing python dictionnaries)
import copy
##operator (for looping easily in a list)
import operator
    
    
    
    
####################################### 
########## function scan_net  #################
#######################################
## -DESCRIPTION :
##    -> recursive function that scans a polygone layer to find the overland flow (OLAF) path following topography.
##         Notice that a polygon can be connected to only ONE element (river or polygon)
## -INPUT : 
##    ->con=pg object containing th ecurrent connection to Postgresql database
##    ->colId=string containing the column name of polygons' id
##    ->colAlt=string containing the column name of polygons' altitude
##    ->map=string containing the name of polygon's map
##    ->forbidden=list containing all polygon' ids which others must not be connected
##    ->in_viaire=list containing all polygon' ids of that are already connected (this list is updtaed all along the function)
##    ->prevCons=dictionnary containing all previous temporary connections (not yet copied in list_newCon)
##    ->prevDone=list containing all previous temporary ids of connected polygons (not yet removed from list_left)
##    ->curId=id of the current polygon to connect
##    ->curAlt=alt of the current polygon to connect
## -OUTPUT :
##    ->list_newCon=a dictionnary that contains all the connections found during function's process
## -CAUTION :
##    ->'in_viaire' and 'list_left' will be updated during all the process of the function
def scan_net(con, colId, colAlt,  colSub , map, subbasin, forbidden, in_viaire, prevCons, prevDone,  curId,  curAlt, list_left, list_newCon={}):
    #testing if the id is still undone
    if curId in  list_left :
        innerCons = {}
        innerDone = []
        #updating temporary variables
        if prevCons:
            innerCons = prevCons.copy()
            innerDone.extend(prevDone)
        #getting neighbours of the current polygon
        neighbours = con.query("SELECT b.\"" + colId + "\", b." + colAlt + " AS Z " +
                                                "FROM \"" + map + "\" AS a, \"" + map + "\" AS b WHERE " +
                                                "a.\"" + colId + "\"=" + str(curId) + " " +
                                                "AND a.\"" + colId + "\"<>b.\"" + colId + "\" " +
                                                "AND a.\"" + colSub + "\"=" + str(subbasin) + " " +
                                                "AND b.\"" + colSub + "\"=" + str(subbasin) + " " +
                                                "AND ST_intersects(a.the_geom, b.the_geom);" ).getresult()
        #getting from 'neighbours' a list of lower polygons already connected (sorted by altitude)
        viaires=sorted([pol for pol in neighbours if (pol[0]  in in_viaire and pol[1]<=curAlt)] , key=operator.itemgetter(1))
        #if 'viaire' contains something : save all the temporaries connections and quit
        if viaires:
            innerCons[curId]=(viaires[0][0], 'pol')
            innerDone.append(curId)
            for i in innerCons.keys(): list_newCon[i]= innerCons[i]
            for i in innerDone: list_left.remove(i)
            in_viaire.extend(innerDone)
                
        #If no lower and already connected polygon in the neighbourood : 
        else:
            #getting from 'neighbours' a list of lower polygons (sorted by altitude)
            polygs = sorted([pol for pol in neighbours if ((pol[0]  not in forbidden) and (pol[0] in list_left) and (pol[0] not in innerDone) and (pol[1]<=curAlt))] , key=operator.itemgetter(1))
            #if 'polygs' contains something : search for the next connection
            if polygs :
                temp=len(in_viaire)
                #we try all the possible ways through all lower neighbours
                for p in polygs :
                    #if a connected polygon has been found : quit
                    if temp<> len(in_viaire): 
                        break
                    #else we call the function to go deeper in the connection tree
                    temp_innerCons ={}
                    temp_innerDone =[]
                    temp_innerCons = innerCons.copy()
                    temp_innerCons[curId] = (p[0], 'pol')
                    temp_innerDone.extend(innerDone)
                    temp_innerDone.append(curId)
                    scan_net(con, colId, colAlt,colSub, map, subbasin, forbidden, in_viaire, temp_innerCons, temp_innerDone, p[0], p[1], list_left)
    #End of the function
    return list_newCon
    list_newCon.clear


    
    
    
##########################
### Class Win : creation of a window ###
##########################
class Win(wx.Frame):
#initializind function of the window
    def __init__(self, parent, id, title, siz):
        wx.Frame.__init__(self, parent, id, title, size=siz)
        panel = wx.Panel(self, -1)
	#font
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)
    #main box
        vbox = wx.BoxSizer(wx.VERTICAL)
    #hbox1 : Land use map map
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'POSTGIS HRU map')
       	self.cb1 = wx.TextCtrl(panel, -1)
        st1.SetFont(font)
        self.cb1.SetFont(font)
        hbox1.Add(st1, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox1.Add(self.cb1, 1)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox12 : River map
        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        st12 = wx.StaticText(panel, -1, 'POSTGIS River map')
       	self.cb12 = wx.TextCtrl(panel, -1)
        st12.SetFont(font)
        self.cb12.SetFont(font)
        hbox12.Add(st12, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox12.Add(self.cb12, 1)
        vbox.Add(hbox12, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox14 : PostgreSql polyg_by_module table
        hbox14 = wx.BoxSizer(wx.HORIZONTAL)
        st14 = wx.StaticText(panel, -1, 'PostgreSql Module table')
       	self.tc14 =wx.TextCtrl(panel, -1)
        st14.SetFont(font)
        self.tc14.SetFont(font)
        hbox14.Add(st14, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox14.Add(self.tc14, 1)
        vbox.Add(hbox14, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox16 : Polygone id
        hbox16 = wx.BoxSizer(wx.HORIZONTAL)
        st16 = wx.StaticText(panel, -1, 'ID column (hru)')
       	self.tc16 =wx.TextCtrl(panel, -1)
        st16.SetFont(font)
        self.tc16.SetFont(font)
        hbox16.Add(st16, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox16.Add(self.tc16, 1)
        vbox.Add(hbox16, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox17 : River id
        hbox17 = wx.BoxSizer(wx.HORIZONTAL)
        st17 = wx.StaticText(panel, -1, 'ID column (river)')
       	self.tc17 =wx.TextCtrl(panel, -1)
        st17.SetFont(font)
        self.tc17.SetFont(font)
        hbox17.Add(st17, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox17.Add(self.tc17, 1)
        vbox.Add(hbox17, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox18 : Subbasin id
        hbox18 = wx.BoxSizer(wx.HORIZONTAL)
        st18 = wx.StaticText(panel, -1, 'ALT. column (hru)')
       	self.tc18 =wx.TextCtrl(panel, -1)
        st18.SetFont(font)
        self.tc18.SetFont(font)
        hbox18.Add(st18, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox18.Add(self.tc18, 1)
        vbox.Add(hbox18, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox15 : Subbasin id
        hbox15 = wx.BoxSizer(wx.HORIZONTAL)
        st15 = wx.StaticText(panel, -1, 'SUB-BASIN column (both)')
       	self.tc15 =wx.TextCtrl(panel, -1)
        st15.SetFont(font)
        self.tc15.SetFont(font)
        hbox15.Add(st15, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox15.Add(self.tc15, 1)
        vbox.Add(hbox15, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox3 : dataBase Name
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, -1, 'db Name')
       	self.tc3 =wx.TextCtrl(panel, -1)
        st3.SetFont(font)
        self.tc3.SetFont(font)
        hbox3.Add(st3, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox3.Add(self.tc3, 1)
        vbox.Add(hbox3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox4 : host Name
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        st4 = wx.StaticText(panel, -1, 'host Name')
       	self.tc4 =wx.TextCtrl(panel, -1, 'localhost')
        st4.SetFont(font)
        self.tc4.SetFont(font)
        hbox4.Add(st4, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox4.Add(self.tc4, 1)
        vbox.Add(hbox4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox5 : port number
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        st5 = wx.StaticText(panel, -1, 'port')
       	self.tc5 =wx.TextCtrl(panel, -1, '5432')
        st5.SetFont(font)
        self.tc5.SetFont(font)
        hbox5.Add(st5, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox5.Add(self.tc5, 1)
        vbox.Add(hbox5, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))        
    #hbox6 : user Name
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, -1, 'user Name')
       	self.tc6 =wx.TextCtrl(panel, -1, 'postgres')
        st6.SetFont(font)
        self.tc6.SetFont(font)
        hbox6.Add(st6, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox6.Add(self.tc6, 1)
        vbox.Add(hbox6, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))        
    #hbox7 : Buttons [Run / Exit]
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(panel,wx.ID_OK,'Run...', size=(70, 30))
        btn2 = wx.Button(panel, wx.ID_EXIT, 'Close', size=(70, 30))
        hbox7.Add(btn1, 0)
        hbox7.Add(btn2, 0, wx.LEFT | wx.BOTTOM , 5)
        vbox.Add(hbox7, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)
	#hbox8 : Execution textBox
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        st8 = wx.StaticText(panel, -1, 'Execution...')
        st8.SetFont(font)
        hbox8.Add(st8, 0)
        vbox.Add(hbox8, 0, wx.LEFT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox9 : Execution textCtrl
        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc9 = wx.TextCtrl(panel, -1, '...', style=wx.TE_MULTILINE)
        hbox9.Add(self.tc9, 1, wx.EXPAND)
        vbox.Add(hbox9, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        vbox.Add((-1, 25))
    #Binding buttons to events
        self.Bind(wx.EVT_BUTTON, self.OnRun, id=btn1.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnQuit, id=btn2.GetId())
    #Self + panel parameters
        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)
        
    #Handled method 'OnRun' called by 'OK' button
    #(contains the effective script)
    def OnRun(self,event):     
    #Get form 's values
        hruStr = self.cb1.GetValue()
        riverStr = self.cb12.GetValue()
        moduleStr = self.tc14.GetValue()
        subStr = self.tc15.GetValue()
        altStr = self.tc18.GetValue()
        polId = self.tc16.GetValue()
        rivId = self.tc17.GetValue()
        dbNameStr = self.tc3.GetValue()
        hostStr = self.tc4.GetValue()
        portStr = self.tc5.GetValue()
        userStr = self.tc6.GetValue()
    #Connection to PostgreSQL database thanks to a pg Object
        myconnexion = pg.connect(dbname=dbNameStr, host=hostStr , port=int(portStr), user=userStr)     
    #1.Searching for viaire polygones
        #detecting intersections between polygones and river segments of a same subbasin
        myconnexion.query("CREATE TABLE olaf_viaire (id serial, id_polyg integer, id_riv integer, polyg_geom geometry);")
        myconnexion.query("INSERT INTO olaf_viaire (id_polyg, id_riv, polyg_geom) " +
                                        "SELECT DISTINCT ON(a.\"" + polId + "\") a.\"" + polId + "\", b.\"" + rivId + "\", a.the_geom " +
                                        "FROM \"" + hruStr + "\" AS a " +
                                        "INNER JOIN \"" + moduleStr + "\" AS c ON (a.new_cod_1=c.id), " +
                                        "\"" + riverStr + "\" AS b WHERE " +
                                        "ST_intersects(a.the_geom,b.the_geom) "+
                                        "AND a.\"" + subStr + "\"=b.\"" + subStr + "\" " +
                                        "AND c.module<>'SIMBA';")
       #detecting intersections between polygones and a SIMBA's one of a same subbasin
        myconnexion.query("CREATE TABLE olaf_simba (id serial, id_polyg integer, id_simba integer, polyg_geom geometry);")
        myconnexion.query("INSERT INTO olaf_simba (id_polyg, id_simba, polyg_geom) " +
                                        "SELECT DISTINCT ON(a.\"" + polId + "\") a.\"" + polId + "\", b.\"" + polId + "\", a.the_geom FROM " +
                                        "\"" + hruStr + "\" AS a, " +
                                        "\"" + hruStr + "\" AS b " +
                                        "INNER JOIN \"" + moduleStr + "\" AS c ON (b.new_cod_1=c.id) " +
                                        "WHERE " +
                                        "ST_intersects(a.the_geom, b.the_geom) " +
                                        "AND a.\"" + subStr + "\"=b.\"" + subStr + "\" " +
                                        "AND a.\"" + altStr + "\">=b.\"" + altStr + "\" " +
                                        "AND a.\"" + polId + "\"<>b.\"" + polId + "\" " +
                                        "AND c.module='SIMBA';")
        self.tc9.Value = "\n\n>> 1:  Postgresql database updated with olaf_viaire and olaf_simba tables."
   #2.Searching for isolated polygones 
        myconnexion.query("CREATE TABLE olaf_isolated (id serial, id_polyg integer, id_connected integer, polyg_geom geometry);")
        myconnexion.query("INSERT INTO olaf_isolated (id_polyg, id_connected, polyg_geom)" +
                                        "SELECT a.\"" + polId + "\" , b.\"" + polId + "\", a.the_geom FROM " +
                                        "\"" + hruStr + "\"  AS a " +
                                        "INNER JOIN \"" + moduleStr + "\" AS f ON (a.new_cod_1=f.id) ," +
                                        "\"" + hruStr + "\"  b WHERE " +
                                        "a.\"" + polId + "\"<>b.\"" + polId + "\" " +
                                        "AND a.\"" + subStr + "\"=b.\"" + subStr + "\" " +
                                        "AND ST_intersects(a.the_geom, b.the_geom) " +
                                        "AND a.\"" + polId + "\" NOT IN (SELECT id_polyg FROM olaf_viaire) " +
                                        "AND a.\"" + polId + "\" NOT IN (SELECT id_polyg FROM olaf_simba) " +
                                        "AND f.module<>'SIMBA' " +
                                        "AND a.\"" + polId + "\" IN (" +
                                            "SELECT c.\"" + polId + "\" FROM (" +
                                                    "SELECT d.\"" + polId + "\", COUNT(e.\"" + polId + "\") FROM " +
                                                    "\"" + hruStr + "\" AS d " +
                                                    "INNER JOIN \"" + moduleStr + "\" AS g ON (d.new_cod_1=g.id) ," +
                                                    "\"" + hruStr + "\"  AS e WHERE " +
                                                    "d.\"" + polId + "\"<>e.\"" + polId + "\" " +
                                                    "AND d.\"" + subStr + "\"=e.\"" + subStr + "\" " +
                                                    "AND ST_intersects(d.the_geom, e.the_geom) " +
                                                    "AND g.module<>'SIMBA' " +
                                                    "GROUP BY d.\"" + polId + "\"" +
                                            ") AS c WHERE count=1 " +
                                        ");")
        self.tc9.Value += "\n\n>> 2:  Postgresql database updated with olaf_isolated table."
   #3.Correction of the map by raising "holes" polygones
        myconnexion.query("UPDATE \"" + hruStr + "\" AS a SET \"" + altStr + "\"=" +
                                        "(SELECT MIN(c.\"" + altStr + "\") FROM \"" + hruStr + "\"  AS c WHERE ST_Intersects(a.the_geom,c.the_geom) AND a.\"" + polId + "\"<>c.\"" + polId + "\") " +
                                        "FROM \"" + moduleStr + "\" AS d "
                                        "WHERE " +
                                        "d.id=a.new_cod_1 " +
                                        "AND d.module<>'SIMBA' " +
                                        "AND a.\"" + altStr + "\"<" +
                                        "("
                                                "SELECT MIN(b.\"" + altStr + "\") FROM " +
                                                "\"" + hruStr + "\"  AS b " +
                                                "INNER JOIN \"" + moduleStr + "\" AS e ON (b.new_cod_1=e.id) "
                                                "WHERE " +
                                                "e.module<>'SIMBA' " +
                                                "AND ST_Intersects(a.the_geom,b.the_geom) " +
                                                "AND a.\"" + polId + "\"<>b.\"" + polId + "\"" +
                                        ")")
        self.tc9.Value += "\n\n>> 3:  Postgresql database updated by raising 'hole' polygons of " + hruStr + " table."
   #4.Scanning network subbasin by subbasin
        connexion={}
        connexionSub={}
        viairesIds =[]
        isolatedIds =[]
        leftIds =[]
       #loop on subbasins
        for j in myconnexion.query("SELECT DISTINCT ON(\"" + subStr + "\") \"" + subStr + "\" FROM \"" + hruStr + "\";").getresult() :
            temp_viaires = []
            temp_left = []
           #getting viaire polygons of the current subbasin
            viaires = myconnexion.query("SELECT a.id_polyg, a.id_riv FROM olaf_viaire AS a;").getresult()
            viaires_simba = myconnexion.query("SELECT a.id_polyg, a.id_simba FROM olaf_simba AS a;").getresult()
            for i in viaires :
               #connecting viaire polygons
                connexion[i[0]] = (i[1] , 'riv')
                viairesIds.append(i[0])            
            for i in viaires_simba :
               #connecting viaire polygons
                connexion[i[0]] = (i[1] , 'simb')
                viairesIds.append(i[0])
           #getting isolated polygons of the current subbsasin
##            isolated = myconnexion.query("SELECT a.id_polyg, a.id_connected, b.\"" + altStr + "\" FROM olaf_isolated AS a "  + 
##                                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_connected=b.id);").getresult()
##            for i in isolated :
##               #connecting isolated polygons
##                connexion[i[0]] = (i[1], 'pol')
##                isolatedIds.append(i[0])
           #getting others polygons of the current subbasin
            left = myconnexion.query("SELECT a.\"" + polId + "\", a.\"" + altStr + "\" FROM " +
                                                    "\"" + hruStr + "\" AS a " +
                                                     "INNER JOIN \"" + moduleStr + "\" AS b ON (a.new_cod_1=b.id) WHERE " +
                                                    "a.\"" + subStr + "\"=" + str(j[0]) + " " +
                                                    "AND b.module<>'SIMBA' " +
                                                    "AND a.\"" + polId + "\" NOT IN (SELECT id_polyg FROM olaf_simba) " +
                                                    "AND a.\"" + polId + "\" NOT IN (SELECT id_polyg FROM olaf_isolated) " +
                                                    "AND a.\"" + polId + "\" NOT IN (SELECT id_polyg FROM olaf_viaire);").getresult()
            for i in left :
                leftIds.append(i[0])
            temp_viaires.extend(viairesIds)
           #scan leaving polygons
            for i in left:
                temp_left = left
                temp=scan_net(myconnexion, polId , altStr, subStr, hruStr, j[0], isolatedIds, temp_viaires, dict(), list(), i[0] , i[1], leftIds) 
                temp_viaires.extend(temp.keys())
                connexionSub.update(temp)
               #if no one polygone is leaving to connect we break the loop
                if len(left)==0 : break
            connexion.update(connexionSub)
            connexionSub.clear()
            del viairesIds[:]
            del isolatedIds [:]
            del leftIds[:]
        self.tc9.Value += "\n\n>> 4:  Scanning the whole map to find the better topologycal routage."
   #5.Filling up table 'olaf_con'
        myconnexion.query("CREATE TABLE olaf_con (id serial, id_polyg integer, id_connected integer, flow_geom geometry DEFAULT NULL, con_type text, CONSTRAINT olaf_con_pkey PRIMARY KEY(id));") 
        for i in connexion.keys():
            myconnexion.query("INSERT INTO olaf_con (id_polyg, id_connected, con_type) VALUES(" +  str(i) + ", " + str(connexion[i][0] ) + ", '" + str(connexion[i][1]) + "');")
        myconnexion.query("UPDATE olaf_con AS a SET flow_geom= " +
                                        "St_GeomFromText( " +
                                                "'LINESTRING(' || ST_X(ST_Centroid(c.the_geom)) || ' ' || ST_Y(ST_Centroid(c.the_geom)) ||  " +
                                                "', ' || ST_X(ST_Centroid(d.the_geom)) || ' ' || ST_Y(ST_Centroid(d.the_geom)) || ')' " +
                                        ")" +
                                        "FROM olaf_con AS b " +
                                        "INNER JOIN \"" + hruStr + "\" AS c ON (b.id_polyg=c.\"" + polId + "\") " +
                                        "INNER JOIN \"" + hruStr + "\" AS d ON (b.id_connected=d.\"" + polId + "\") WHERE " +
                                        "a.id=b.id " +
                                        "AND (b.con_type='pol' OR b.con_type='simb')" )
        myconnexion.query("UPDATE olaf_con AS a SET flow_geom= " +
                                        "St_GeomFromText( " +
                                                "'LINESTRING(' || ST_X(ST_Centroid(c.the_geom)) || ' ' || ST_Y(ST_Centroid(c.the_geom)) ||  " +
                                                "', ' || ST_X(ST_ClosestPoint(d.the_geom,ST_Centroid(c.the_geom)))  || ' ' || ST_Y(ST_ClosestPoint(d.the_geom,ST_Centroid(c.the_geom)))  || ')' " +
                                        ")" +
                                        "FROM olaf_con AS b " +
                                        "INNER JOIN \"" + hruStr + "\" AS c ON (b.id_polyg=c.\"" + polId + "\") " +
                                        "INNER JOIN \"" + riverStr + "\" AS d ON (b.id_connected=d.\"" + rivId + "\")" +
                                        "WHERE " +
                                        "a.id=b.id " +
                                        "AND (b.con_type='riv')")
        self.tc9.Value += "\n\n>> 5:  PostgreSQL table 'olaf_con' filled up with natural connexions."
    #6.Manual corrections for unconnected polygones that touches a olaf_viaire one
        myconnexion.query("CREATE TABLE olaf_pseudo_isolated (id serial, id_polyg integer, polyg_geom geometry, CONSTRAINT olaf_pseudo_isolated_pkey PRIMARY KEY(id));") 
        self.tc9.Value += "\n\n>> 6:  PostgreSQL table 'olaf_con' completed with pseudo isolated polygones."
    #7.Filling up table 'olaf_uncon'
        myconnexion.query("CREATE TABLE olaf_uncon (id serial, id_polyg integer , polyg_geom geometry, CONSTRAINT olaf_uncon_pkey PRIMARY KEY(id));") 
        myconnexion.query("INSERT INTO olaf_uncon  (id_polyg, polyg_geom)" +
                                        "SELECT a.\"" + polId + "\", a.the_geom " +
                                        "FROM \"" + hruStr + "\" AS a INNER JOIN \"" + moduleStr + "\" AS c ON (a.new_cod_1=c.id) WHERE " +
                                        "a.\"" + polId + "\" NOT IN(SELECT b.id_polyg FROM olaf_con AS b)" +
                                        "AND c.module<>'SIMBA'")
        self.tc9.Value += "\n\n>> 7:  PostgreSQL table 'olaf_uncon' created and filled up."
    #8.Creating table for each type of connexion

                                        
########################    IF MODULE FRER1D      ############################
#####      don't forget to use the rigth module_ids table and decomment lines below   ##############
####################################################################
##        myconnexion.query("CREATE TABLE olaf_frer1d2river (id serial CONSTRAINT olaf_frer1d2river_pkey PRIMARY KEY, id_polyg integer , id_riv integer, flow_geom geometry)")
##        myconnexion.query("INSERT INTO olaf_frer1d2river (id_polyg, id_riv, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS c ON (b.new_cod_1=c.id) " +
##                                        "WHERE c.module='FRER1D' "
##                                        "AND a.con_type='riv';" )
##        myconnexion.query("CREATE TABLE olaf_frer1d2simba (id serial CONSTRAINT olaf_frer1d2simba_pkey PRIMARY KEY, id_polyg integer , id_simba integer, flow_geom geometry)")
##        myconnexion.query("INSERT INTO olaf_frer1d2simba (id_polyg, id_simba, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS c ON (b.new_cod_1=c.id) " +
##                                        "WHERE c.module='FRER1D' "
##                                        "AND a.con_type='simb';" )
##        myconnexion.query("CREATE TABLE olaf_frer1d2frer1d (id serial CONSTRAINT olaf_frer1d2frer1d_pkey PRIMARY KEY, id_polyg integer , id_connected integer, flow_geom geometry)")
##        myconnexion.query("INSERT INTO olaf_frer1d2frer1d (id_polyg, id_connected, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + hruStr + "\" AS c ON (a.id_connected=c.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS d ON (b.new_cod_1=d.id) " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS e ON (c.new_cod_1=e.id) " +
##                                        "WHERE " +
##                                        "d.module='FRER1D' " +
##                                        "AND e.module='FRER1D' " +
##                                        "AND a.con_type='pol';" )
##        myconnexion.query("CREATE TABLE olaf_frer1d2urbs (id serial CONSTRAINT olaf_frer1d2urbs_pkey PRIMARY KEY, id_polyg integer , id_connected integer, flow_geom geometry)")
##        myconnexion.query("INSERT INTO olaf_frer1d2urbs (id_polyg, id_connected, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + hruStr + "\" AS c ON (a.id_connected=c.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS d ON (b.new_cod_1=d.id) " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS e ON (c.new_cod_1=e.id) " +
##                                        "WHERE " +
##                                        "d.module='FRER1D' " +
##                                        "AND e.module='URBS' " +
##                                        "AND a.con_type='pol';" )
##        myconnexion.query("INSERT INTO olaf_frer1d2urbs (id_polyg, id_connected, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + hruStr + "\" AS c ON (a.id_connected=c.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS d ON (b.new_cod_1=d.id) " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS e ON (c.new_cod_1=e.id) " +
##                                        "WHERE " +
##                                        "d.module='URBS' " +
##                                        "AND e.module='FRER1D' " +
##                                        "AND a.con_type='pol';" )
##        myconnexion.query("CREATE TABLE olaf_frer1d2hedge (id serial CONSTRAINT olaf_frer1d2hedge_pkey PRIMARY KEY, id_polyg integer , id_connected integer, flow_geom geometry)")
##        myconnexion.query("INSERT INTO olaf_frer1d2hedge (id_polyg, id_connected, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + hruStr + "\" AS c ON (a.id_connected=c.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS d ON (b.new_cod_1=d.id) " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS e ON (c.new_cod_1=e.id) " +
##                                        "WHERE " +
##                                        "d.module='FRER1D' " +
##                                        "AND e.module='HEDGE' " +
##                                        "AND a.con_type='pol';" )
##        myconnexion.query("INSERT INTO olaf_frer1d2hedge (id_polyg, id_connected, flow_geom) "  + 
##                                        "SELECT a.id_polyg, a.id_connected, a.flow_geom FROM olaf_con AS a " +
##                                        "INNER JOIN \"" + hruStr + "\" AS b ON (a.id_polyg=b.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + hruStr + "\" AS c ON (a.id_connected=c.\"" + polId +"\") " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS d ON (b.new_cod_1=d.id) " +
##                                        "INNER JOIN \"" + moduleStr + "\" AS e ON (c.new_cod_1=e.id) " +
##                                        "WHERE " +
##                                        "d.module='HEDGE' " +
##                                        "AND e.module='FRER1D' " +
##                                        "AND a.con_type='pol';" )
#####################################################################

        self.tc9.Value += "\n\n>> 8: PostgreSQL database updated with tables for each types of connection."
    #8.Put tables in schema 'olaf'
        myconnexion.query("CREATE SCHEMA olaf;")
        self.tc9.Value += "\n\n>> 8:  New PostgreSQL schema 'olaf' created."
    #9.Put tables in schema 'olaf'
        myconnexion.query("ALTER TABLE olaf_viaire SET SCHEMA olaf")
        myconnexion.query("ALTER TABLE olaf_simba SET SCHEMA olaf")
        myconnexion.query("ALTER TABLE olaf_isolated SET SCHEMA olaf")
        myconnexion.query("ALTER TABLE olaf_pseudo_isolated SET SCHEMA olaf")
        myconnexion.query("ALTER TABLE olaf_con SET SCHEMA olaf")
        myconnexion.query("ALTER TABLE olaf_uncon SET SCHEMA olaf")
        self.tc9.Value += "\n\n>> 9:  Tables moved in 'olaf' Schema."
        
########################    IF MODULE FRER1D      ############################
#####      don't forget to use the rigth module_ids table and decomment lines below   ##############
####################################################################
##        myconnexion.query("ALTER TABLE olaf_frer1d2river SET SCHEMA olaf")
##        myconnexion.query("ALTER TABLE olaf_frer1d2simba SET SCHEMA olaf")
##        myconnexion.query("ALTER TABLE olaf_frer1d2frer1d SET SCHEMA olaf")
##        myconnexion.query("ALTER TABLE olaf_frer1d2hedge SET SCHEMA olaf")
##        myconnexion.query("ALTER TABLE olaf_frer1d2urbs SET SCHEMA olaf")
####################################################################
    
        self.tc9.Value += "\n\nDONE !!!"
        print(self.tc9.Value)
        myconnexion.close()

#Handled method 'OnQuit'
    def OnQuit(self, event):
        self.Close()

  

##############
###      Main       ###     
##############
app = wx.App()
Win(None, -1, 'interfOlaf.py', (460, 800))
app.MainLoop()




