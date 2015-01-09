#!/usr/bin/env python
#Create new subset of polygon with a Convexity Index Threshold

'''-------------------- conUhe.py ---------------------
   -created by : Florent BROSSARD
   -date : 15/12/2010
---------------------------------------------------------------
'''

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

try:
    import grass.script as grass
except ImportError:
    raise ImportError,"The grass.script module is required to run this program"
    
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
##    -> recursive function that scans a polygone layer to find a topological routage of the uhes.
##         Notice that an uhe can be connected to only ONE element (river or uhe)
## -INPUT : 
##    ->con=pg object to use SQL queries in the function
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
def scan_net(con, colId, colAlt, module , map, forbidden, in_viaire, prevCons, prevDone,  curId,  curAlt, list_left, list_newCon={}):
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
                                                "FROM \"" + map + "\" AS a " +
                                                "INNER JOIN " +  module + " AS c ON (a.new_cod_1 = c.id), " +
                                                "\"" + map + "\" AS b "
                                                "INNER JOIN " +  module + " AS d ON (b.new_cod_1 = d.id) WHERE " +
                                                "a.\"" + colId + "\"=" + str(curId) + " " +
                                                "AND c.module='URBS' " +
                                                "AND d.module='URBS' " +
                                                "AND a.\"" + colId + "\"<>b.\"" + colId + "\" " +
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
                    scan_net(con, colId, colAlt, module, map,forbidden, in_viaire, temp_innerCons, temp_innerDone, p[0], p[1], list_left)
    #End of the function
    return list_newCon
    list_newCon.clear


    
    
    
##########################
### Class Win : creation of a window ###
##########################
# Class Win : creation of a window
class Win(wx.Frame):
#init
    def __init__(self, parent, id, title, siz):
        wx.Frame.__init__(self, parent, id, title, size=siz)
        panel = wx.Panel(self, -1)
	#font
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)
	#main box
        vbox = wx.BoxSizer(wx.VERTICAL)
	#hbox2 : polyg map
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, -1, 'POSTGIS HRU map')
       	self.tc2 =wx.TextCtrl(panel, -1)
        st2.SetFont(font)
        self.tc2.SetFont(font)
        hbox2.Add(st2, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox2.Add(self.tc2, 1)
        vbox.Add(hbox2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox1 : River map
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'POSTGIS river map')
       	self.tc1 =wx.TextCtrl(panel, -1)
        st1.SetFont(font)
        self.tc1.SetFont(font)
        hbox1.Add(st1, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox1.Add(self.tc1, 1)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox13 : PostgreSql polyg_by_module table
        hbox13 = wx.BoxSizer(wx.HORIZONTAL)
        st13 = wx.StaticText(panel, -1, 'PostgreSql Module table')
       	self.tc13 =wx.TextCtrl(panel, -1)
        st13.SetFont(font)
        self.tc13.SetFont(font)
        hbox13.Add(st13, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox13.Add(self.tc13, 1)
        vbox.Add(hbox13, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox11 : HRU id column
        hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        st11 = wx.StaticText(panel, -1, 'ID column (hru)')
       	self.tc11 =wx.TextCtrl(panel, -1)
        st11.SetFont(font)
        self.tc11.SetFont(font)
        hbox11.Add(st11, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox11.Add(self.tc11, 1)
        vbox.Add(hbox11, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox10 : River id column
        hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        st10 = wx.StaticText(panel, -1, 'ID column (river)')
       	self.tc10 =wx.TextCtrl(panel, -1)
        st10.SetFont(font)
        self.tc10.SetFont(font)
        hbox10.Add(st10, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox10.Add(self.tc10, 1)
        vbox.Add(hbox10, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox12 : Uhe id column
        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        st12 = wx.StaticText(panel, -1, 'ALT. column (hru)')
       	self.tc12 =wx.TextCtrl(panel, -1)
        st12.SetFont(font)
        self.tc12.SetFont(font)
        hbox12.Add(st12, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox12.Add(self.tc12, 1)
        vbox.Add(hbox12, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
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
       	self.tc4 =wx.TextCtrl(panel, -1,  'localhost')
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
       	self.tc6 =wx.TextCtrl(panel, -1,  'postgres')
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
    #Binding
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
        uheStr = self.tc2.GetValue()
        riverStr = self.tc1.GetValue()
        uheId = self.tc11.GetValue()
        riverId = self.tc10.GetValue()
        altId = self.tc12.GetValue()
        moduleStr = self.tc13.GetValue()
        dbNameStr = self.tc3.GetValue()
        hostStr = self.tc4.GetValue()
        portStr = self.tc5.GetValue()
        userStr = self.tc6.GetValue()
    #Connection to PostgreSQL database thanks to a pg Object
        myconnexion = pg.connect(dbname=dbNameStr, host=hostStr , port=int(portStr), user=userStr)
    #1.Searching for viaire polygones
        #detecting intersections between polygones and river segments of a same subbasin
        myconnexion.query("CREATE TABLE uhe_viaire (id serial, id_polyg integer, id_riv integer, polyg_geom geometry);")
        myconnexion.query("INSERT INTO uhe_viaire (id_polyg, id_riv, polyg_geom) " +
                                        "SELECT DISTINCT ON(a.\"" + uheId + "\") a.\"" + uheId + "\", b.\"" + riverId + "\", a.the_geom " +
                                        "FROM \"" + uheStr + "\" AS a " +
                                        "INNER JOIN \"" + moduleStr + "\" AS c ON (a.new_cod_1=c.id), " +
                                        "\"" + riverStr + "\" AS b WHERE " +
                                        "ST_intersects(a.the_geom,b.the_geom) "+
                                        "AND c.module='URBS';")
        self.tc9.Value = "\n\n>> 1:  Postgresql database updated with uhe_viaire table."
   #2.Searching for isolated polygones 
        myconnexion.query("CREATE TABLE uhe_isolated (id serial, id_polyg integer, id_connected integer, polyg_geom geometry);")
        myconnexion.query("INSERT INTO uhe_isolated (id_polyg, id_connected, polyg_geom)" +
                                        "SELECT a.\"" + uheId + "\" , b.\"" + uheId + "\", a.the_geom FROM " +
                                        "\"" + uheStr + "\"  AS a " +
                                        "INNER JOIN \"" + moduleStr + "\" AS f ON (a.new_cod_1=f.id) ," +
                                        "\"" + uheStr + "\" AS b " +
                                        "INNER JOIN \"" + moduleStr + "\" AS h ON (b.new_cod_1=h.id) WHERE " +
                                        "a.\"" + uheId + "\"<>b.\"" + uheId + "\" " +
                                        "AND ST_intersects(a.the_geom, b.the_geom) " +
                                        "AND a.\"" + uheId + "\" NOT IN (SELECT id_polyg FROM uhe_viaire) " +
                                        "AND f.module='URBS' " +
                                        "AND h.module='URBS' " +
                                        "AND a.\"" + uheId + "\" IN (" +
                                            "SELECT c.\"" + uheId + "\" FROM (" +
                                                    "SELECT d.\"" + uheId + "\", COUNT(e.\"" + uheId + "\") FROM " +
                                                    "\"" + uheStr + "\" AS d " +
                                                    "INNER JOIN \"" + moduleStr + "\" AS g ON (d.new_cod_1=g.id) ," +
                                                    "\"" + uheStr + "\"  AS e " +
                                                    "INNER JOIN \"" + moduleStr + "\" AS i ON (b.new_cod_1=i.id) WHERE " +
                                                    "d.\"" + uheId + "\"<>e.\"" + uheId + "\" " +
                                                    "AND ST_intersects(d.the_geom, e.the_geom) " +
                                                    "AND g.module='URBS' " +
                                                    "AND i.module='URBS' " +
                                                    "GROUP BY d.\"" + uheId + "\"" +
                                            ") AS c WHERE count=1 " +
                                        ");")
        self.tc9.Value += "\n\n>> 2:  Postgresql database updated with uhe_isolated table."
   #3.Scanning network
        connexion={}
        viairesIds =[]
        isolatedIds =[]
        leftIds =[]
        temp_viaires = []
        temp_left = []
       #getting viaire polygons
        viaires = myconnexion.query("SELECT id_polyg, id_riv FROM uhe_viaire;").getresult()
        for i in viaires :
           #connecting viaire polygons
            connexion[i[0]] = (i[1] , 'riv')
            viairesIds.append(i[0])            
       #getting isolated polygons
        isolated = myconnexion.query("SELECT a.id_polyg, a.id_connected, b.\"" + altId + "\" FROM uhe_isolated AS a "  + 
                                                    "INNER JOIN \"" + uheStr + "\" AS b ON (a.id_connected=b.id);").getresult()
        for i in isolated :
           #connecting isolated polygons
            connexion[i[0]] = (i[1], 'pol')
            isolatedIds.append(i[0])
       #getting others polygons
        left = myconnexion.query("SELECT a.\"" + uheId + "\", a.\"" + altId + "\" FROM " +
                                                "\"" + uheStr + "\" AS a " +
                                                 "INNER JOIN \"" + moduleStr + "\" AS b ON (a.new_cod_1=b.id) WHERE " +
                                                "b.module='URBS' " +
                                                "AND a.\"" + uheId + "\" NOT IN (SELECT id_polyg FROM uhe_isolated) " +
                                                "AND a.\"" + uheId + "\" NOT IN (SELECT id_polyg FROM uhe_viaire);").getresult()
        for i in left :
            leftIds.append(i[0])
        temp_viaires.extend(viairesIds)
       #scan leaving polygons
        for i in left:
            temp_left = left
            temp=scan_net(myconnexion, uheId , altId, moduleStr, uheStr, isolatedIds, temp_viaires, dict(), list(), i[0] , i[1], leftIds) 
            temp_viaires.extend(temp.keys())
            connexion.update(temp)
           #if no one polygone is leaving to connect we break the loop
            if len(left)==0 : break
        self.tc9.Value += "\n\n>> 3:  Scanning the whole map to find the better topologycal routage."
    #5.Filling up table 'olaf_con'
        myconnexion.query("CREATE TABLE uhe_con (id serial, id_polyg integer, id_connected integer, con_type text, id_river integer DEFAULT -1, polyg_geom geometry DEFAULT NULL, CONSTRAINT uhe_con_pkey PRIMARY KEY(id));") 
        for i in connexion.keys():
            myconnexion.query("INSERT INTO uhe_con (id_polyg, id_connected, con_type) VALUES(" +  str(i) + ", " + str(connexion[i][0] ) + ", '" + str(connexion[i][1]) + "');")
        self.tc9.Value += "\n\n>> 5:  PostgreSQL table 'uhe_con' filled up with natural connexions."
    #6.Manual corrections for unconnected polygones 
        myconnexion.query("CREATE TABLE uhe_pseudo_isolated (id serial, id_polyg integer, polyg_geom geometry, CONSTRAINT uhe_pseudo_isolated_pkey PRIMARY KEY(id));") 
        myconnexion.query("INSERT INTO uhe_pseudo_isolated(id_polyg, polyg_geom) " +
                                                "(SELECT " +
                                                "a.\"" + uheId + "\", " +
                                                "a.the_geom " +
                                                "FROM \"" + uheStr + "\" AS a " +
                                                "INNER JOIN \"" + moduleStr + "\" AS b ON (a.new_cod_1=b.id) WHERE "
                                                "b.module='URBS' " +
                                                "AND a.\"" + uheId + "\" NOT IN (SELECT id_polyg FROM uhe_con)" +
                                                ");")
        myconnexion.query("INSERT INTO uhe_con (id_polyg, id_connected, con_type) " +
                                       "(SELECT DISTINCT ON(a.\"" + uheId + "\")" +
                                       "a.\"" + uheId + "\", " +
                                       "b.\"" + riverId + "\", " +
                                       "'riv' " +
                                       "FROM \"" + uheStr + "\" AS a ," +
                                       "\""+ riverStr + "\" AS b WHERE " +
                                       "a.\"" + uheId + "\" IN (SELECT id_polyg FROM uhe_pseudo_isolated) " +
                                       "AND ST_distance(a.the_geom,b.the_geom) = " +
                                                "(SELECT MIN(ST_distance(a.the_geom,c.the_geom)) FROM \""+ riverStr + "\" AS c)" +
                                        ");")
        self.tc9.Value += "\n\n>> 6:  PostgreSQL table 'olaf_con' completed with pseudo isolated polygones."
   #6.Detecting the "final" connection with a river segment
        myconnexion.query("UPDATE uhe_con AS a SET id_river=a.id_connected WHERE a.con_type='riv'")
        for i in  myconnexion.query("SELECT id, id_polyg, id_connected FROM uhe_con WHERE id_river=-1").getresult() :
            tempUhe=i[2]
            while 1 :
                tempfinal = myconnexion.query("SELECT id_connected,con_type FROM uhe_con WHERE id_polyg=" + str(tempUhe) ).getresult()
                tempUhe = tempfinal[0][0]
                if tempfinal[0][1] =='riv' : break
            myconnexion.query("UPDATE uhe_con SET id_river=" + str(tempUhe) + " WHERE id="+ str(i[0]) )
        self.tc9.Value += "\n\n>> 6: PostgreSQL table 'uhe_con' updated with the final river id."
    #7.Get polygons geometry
        myconnexion.query("UPDATE uhe_con AS a SET polyg_geom=b.the_geom FROM \"" + uheStr + "\" AS b WHERE b.\"" + uheId + "\"=a.id_polyg" )
        self.tc9.Value += "\n\n>> 7: PostgreSQL table 'uhe_con' updated with the geometry of polygons."
    #8.Put tables in schema 'uhe'
        myconnexion.query("CREATE SCHEMA uhe;")
        self.tc9.Value += "\n\n>> 8:  New PostgreSQL schema 'uhe' created."
    #9.Put tables in schema 'uhe
        myconnexion.query("ALTER TABLE uhe_viaire SET SCHEMA uhe")
        myconnexion.query("ALTER TABLE uhe_isolated SET SCHEMA uhe")
        myconnexion.query("ALTER TABLE uhe_pseudo_isolated SET SCHEMA uhe")
        myconnexion.query("ALTER TABLE uhe_con SET SCHEMA uhe")
        myconnexion.query("CREATE TABLE uhe.\"" + moduleStr + "\" AS SELECT * FROM \"" + moduleStr + "\"")
        myconnexion.query("CREATE TABLE uhe.\"" + uheStr + "\" AS SELECT * FROM \"" + uheStr + "\"")
        myconnexion.query("CREATE TABLE uhe.\"" + riverStr + "\" AS SELECT * FROM \"" + riverStr + "\"")
        self.tc9.Value += "\n\n>> 9:  Tables moved in 'uhe' Schema."

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
Win(None, -1, 'conUhe.py', (430, 800))
app.MainLoop()


