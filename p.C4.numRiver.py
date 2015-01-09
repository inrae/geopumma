#!!usr/bin/env python

'''-------------------- numRiver.py ---------------------
   -created by : Florent BROSSARD
   -date : 30/11/2010
--------------------------------------------------------------
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
    
    


#Recursive function that scan network node by node, branch by branch
def Scan_network(colId, colName,  map,  con, list_newIds, nextId, riverId, list_done=[]):
    if len(list_newIds)!=0: 
        if riverId != list_newIds[len(list_newIds)-1][2]: 
            del list_done[:]
    if len(list_done)==0:
        list_newIds.append((nextId,len(list_newIds)+1, riverId))
        list_done.append(nextId)
    neighb = con.query("SELECT b.\"" +  colId + "\", ST_distance(ST_EndPoint(a.the_geom),ST_Intersection(a.the_geom, b.the_geom)) AS priority " + 
                                    "FROM " + map + " AS a, " + map + " AS b WHERE " +
                                        "b.\"" + colName + "\"=" + str(riverId) + " " +
                                        "AND (a.\"" +  colId + "\"=" + str(nextId) + ") " +
                                        "AND (a.\"" +  colId + "\" <> b.\"" +  colId + "\") " +
                                        "AND (ST_Touches(a.the_geom, b.the_geom)) " +
                                    "ORDER BY priority").getresult()
    for i in neighb: 
        if i[0] not in list_done:
            list_newIds.append((int(i[0]),len(list_newIds)+1, riverId))
            list_done.append(int(i[0]))
            Scan_network(colId, colName, map, con, list_newIds , int(i[0]), riverId)
    

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
	#hbox1 : River map
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'River POSTGIS layer')
       	self.cb1 = wx.TextCtrl(panel, -1)
        st1.SetFont(font)
        self.cb1.SetFont(font)
        hbox1.Add(st1, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox1.Add(self.cb1, 1)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox2 : Outlet map
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, -1, 'Outlet POSTGIS layer')
       	self.cb2 =wx.TextCtrl(panel, -1)
        st2.SetFont(font)
        self.cb2.SetFont(font)
        hbox2.Add(st2, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox2.Add(self.cb2, 1)
        vbox.Add(hbox2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox17 : River id
        hbox17 = wx.BoxSizer(wx.HORIZONTAL)
        st17 = wx.StaticText(panel, -1, 'River column ID')
       	self.tc17 =wx.TextCtrl(panel, -1)
        st17.SetFont(font)
        self.tc17.SetFont(font)
        hbox17.Add(st17, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox17.Add(self.tc17, 1)
        vbox.Add(hbox17, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox10 : River ID in River layer
        hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        st10 = wx.StaticText(panel, -1, 'River column RIVER_ID')
       	self.cb10 = wx.TextCtrl(panel, -1)
        st10.SetFont(font)
        self.cb10.SetFont(font)
        hbox10.Add(st10, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox10.Add(self.cb10, 1)
        vbox.Add(hbox10, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
	#hbox11 : River ID in Outlet layer
        hbox11 = wx.BoxSizer(wx.HORIZONTAL)
        st11 = wx.StaticText(panel, -1, 'Outlet column RIVER_ID')
       	self.cb11 = wx.TextCtrl(panel, -1)
        st11.SetFont(font)
        self.cb11.SetFont(font)
        hbox11.Add(st11, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox11.Add(self.cb11, 1)
        vbox.Add(hbox11, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox3 : bdName Name
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, -1, 'bdName')
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

        
#method 'OnRun'
    def OnRun(self,event):     
   #Get form's values
        filvoirie =  self.cb1.GetValue()
        outletmap = self.cb2.GetValue()
        rivId =  self.tc17.GetValue()
        IDfilvoirie =  self.cb10.GetValue()
        IDoutlet = self.cb11.GetValue()
        dbNameStr = self.tc3.GetValue()
        hostStr = self.tc4.GetValue()
        portStr = self.tc5.GetValue()
        userStr = self.tc6.GetValue()
        
        myconnexion = pg.connect(dbname=dbNameStr, host=hostStr , port=int(portStr), user=userStr)
      #1.Pre-processing of tables
        myconnexion.query("ALTER TABLE \"" + filvoirie + "\" ADD COLUMN ordered_id integer; ")
        self.tc9.Value = ">> 1: PostgreSQL table '" + filvoirie + "' updated by adding the column 'ordered_id'."
    #2.Numbering segments
        #getting the list of outlets to loop on corresponding rivers
        listOutlet = myconnexion.query("SELECT \"" + IDoutlet + "\" FROM \"" + outletmap + "\" ORDER BY \"" + IDoutlet + "\"").getresult()
        listNewId =[]
        temp =""
        #looping from a river to another
        for outlet in listOutlet:
            #searching for the river segment touching the outlet
            idstart= myconnexion.query("SELECT a.\"" + rivId + "\"  FROM \"" + filvoirie + "\" AS a, \"" + outletmap + "\" AS b WHERE " + 
                                                        "b.\"" + IDoutlet + "\"=" + str(outlet[0]) +\
                                                        " AND (touches(a.the_geom,b.the_geom))").getresult()
            #if river segment found
            if idstart:
                Scan_network(rivId, IDfilvoirie, filvoirie,  myconnexion, listNewId, int(idstart[0][0]), outlet[0])
            #if not : topological error between outlets and river maps
            else:
                temp += ("\n     > ERROR: outlet " + str(outlet[0]) + " is touched by no segment.")
        self.tc9.Value += ("\n\n>> 2: Scan of the network finished : "+ str(len(listNewId)) +" on " +
                             str(myconnexion.query("SELECT COUNT(*) FROM \"" + filvoirie + "\";").getresult()[0][0]) +
                            " segments will be udpated.")
        self.tc9.Value += temp
    #3.Updating river map
        for i in listNewId:
            myconnexion.query("UPDATE \"" + filvoirie + "\" SET ordered_id="+ str(i[1]) +" WHERE \"" + rivId + "\"=" + str(i[0]))
        self.tc9.Value += "\n\n>> 3: PostgreSQL table '" + filvoirie + "' updated with ordered ids."
        self.tc9.Value += "\n\n>> Done !!!."
        
        print(self.tc9.Value)
        myconnexion.close()
        
#Handled method 'OnQuit'
    def OnQuit(self, event):
        self.Close()

  

##############
###      Main       ###     
##############
app = wx.App()
Win(None, -1, 'numRiver.py', (430, 550))
app.MainLoop()
