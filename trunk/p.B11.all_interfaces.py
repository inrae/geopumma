#!/usr/bin/env python
#
############################################################################
#
# MODULE        : p.all_interfaces.py
# AUTHOR(S)     : Florent B. 10/01/2011
# MODIFYED BY   : Sanzana P. 01/12/2014
#               
# PURPOSE       : Identifying and extracting of all interfaces (WTI & WTRI)
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

#####################################
######### Importing librairies  #####
#####################################
##wx (for graphical interface)
try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"
##grass.script (to use grass functions)
try:
    import grass.script as grass
except ImportError:
    raise ImportError,"The grass.script module is required to run this program"
##pg (to use postgresql queries)
try:
    import pg
except ImportError:
    raise ImportError,"The pygresql (pg) module is required to run this program"
    
    
    
    
########################################
### Class Win : creation of a window ###
########################################
class Win(wx.Frame):
#initializind function of the window
    def __init__(self, parent, id, title, siz):
        wx.Frame.__init__(self, parent, id, title, size=siz)
        panel = wx.Panel(self, -1)
    #get the list of all grass maps
        vector_list = grass.list_strings('vect')
        raster_list = grass.list_strings('rast')
	#font
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)
    #main box
        vbox = wx.BoxSizer(wx.VERTICAL)
    #hbox1 : Land_use map
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'GRASS HRU map')
       	self.cb1 = wx.ComboBox(panel, -1, choices=vector_list, value=vector_list[0], size=(310, 30), style=wx.CB_READONLY)
        st1.SetFont(font)
        self.cb1.SetFont(font)
        hbox1.Add(st1, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox1.Add(self.cb1, 1)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox12 : River map
        hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        st12 = wx.StaticText(panel, -1, 'GRASS River map')
       	self.cb12 = wx.ComboBox(panel, -1, choices=vector_list, value=vector_list[0], size=(310, 30), style=wx.CB_READONLY)
        st12.SetFont(font)
        self.cb12.SetFont(font)
        hbox12.Add(st12, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox12.Add(self.cb12, 1)
        vbox.Add(hbox12, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))
    #hbox2 : PostgreSql module ids table
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, -1, 'PostgreSql module ids table')
       	self.tc2 =wx.TextCtrl(panel, -1, 'module_ids')
        st2.SetFont(font)
        self.tc2.SetFont(font)
        hbox2.Add(st2, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox2.Add(self.tc2, 1)
        vbox.Add(hbox2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))    
    #hbox14 : id polygon
        hbox14= wx.BoxSizer(wx.HORIZONTAL)
        st14 = wx.StaticText(panel, -1, 'Polygon column ID')
       	self.tc14 =wx.TextCtrl(panel, -1, 'id')
        st14.SetFont(font)
        self.tc14.SetFont(font)
        hbox14.Add(st14, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox14.Add(self.tc14, 1)
        vbox.Add(hbox14, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10))     
    #hbox15 : id river reach
        hbox15= wx.BoxSizer(wx.HORIZONTAL)
        st15 = wx.StaticText(panel, -1, 'River column ID')
       	self.tc15 =wx.TextCtrl(panel, -1, 'id')
        st15.SetFont(font)
        self.tc15.SetFont(font)
        hbox15.Add(st15, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox15.Add(self.tc15, 1)
        vbox.Add(hbox15, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10)) 
    #hbox16 : columng manning
        hbox16= wx.BoxSizer(wx.HORIZONTAL)
        st16 = wx.StaticText(panel, -1, 'River column MANNING')
       	self.tc16 =wx.TextCtrl(panel, -1, 'manning')
        st16.SetFont(font)
        self.tc16.SetFont(font)
        hbox16.Add(st16, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox16.Add(self.tc16, 1)
        vbox.Add(hbox16, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add((-1, 10)) 
    #hbox11 : Location of cvs file
        hbox11= wx.BoxSizer(wx.HORIZONTAL)
        st11 = wx.StaticText(panel, -1, 'Location of cvs file')
       	self.tc11 =wx.TextCtrl(panel, -1, 'c:\...\modules.csv')
        st11.SetFont(font)
        self.tc11.SetFont(font)
        hbox11.Add(st11, 0, wx.RIGHT| wx.BOTTOM , 8)
        hbox11.Add(self.tc11, 1)
        vbox.Add(hbox11, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
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
        landUseStr = self.cb1.GetValue().split("@",0)
        riverStr = self.cb12.GetValue().split("@",0)
##       HRUboundaries = self.cb13.GetValue().split("@",0)
        ##rasterStr = self.cb13.GetValue().split("@",0)
        moduleStr = self.tc2.GetValue()
        raiz= self.tc11.GetValue()
        polygId=self.tc14.GetValue()
        rivId=self.tc15.GetValue()
        manningId=self.tc16.GetValue()
        dbNameStr = self.tc3.GetValue()
        hostStr = self.tc4.GetValue()
        portStr = self.tc5.GetValue()
        userStr = self.tc6.GetValue()
        myconnexion = pg.connect(dbname=dbNameStr, host=hostStr , port=int(portStr), user=userStr)        
    #1.Researching for interfaces 
        #getting boundaries of polygon map
        grass.run_command("v.category", input=landUseStr, output='interfaces', layer=2, type='boundary', option='add',  overwrite=True)
        #getting neighbours ids of boundaries
        grass.run_command("v.db.addtable",  map='interfaces', layer=2,  col='left integer, right integer')
        grass.run_command("v.to.db",  map='interfaces', layer=2,  option='sides', col=['left', 'right'])
	#grass.run_command("db.out.ogr.py",input='interfaces', dsn='modules', format='CSV',overwrite=True)


	#raiz='c:\Lyon_2014_psanzana\Scripts\modules\modules.csv'
	#modules csv must have column cat_tmp equal to cat

	grass.run_command("db.in.ogr.py",dsn=raiz, output='modules_table',overwrite=True)

	grass.run_command("v.db.join.py", map='interfaces',col='left', otable='modules_table',ocol='cat_tmp',layer=2)
	grass.run_command("v.db.renamecolumn.py", map='interfaces', column='module,mod_a', layer=2)
	grass.run_command("v.db.dropcolumn.py", map='interfaces',layer=2,column='cat_tmp')
	grass.run_command("v.db.join.py", map='interfaces',col='right',otable='modules_table',ocol='cat_tmp',layer=2)
	grass.run_command("v.db.renamecolumn.py", map='interfaces',column='module,mod_b',layer=2)
	grass.run_command("v.db.dropcolumn.py", map='interfaces',layer=2,column='cat_tmp')

 
###        grass.run_command("v.db.addcol", map='interfaces', layer=2, col="meanheight double")
###        grass.run_command("v.edit",  map='interfaces', layer=2,  tool='delete',  where='left=-1 or rigth=-1')
###        grass.run_command("g.region",rast=rasterStr)
###        list_ditch = grass.read_command("v.db.select",map='interfaces', layer=2, col='cat',flags='c')
###        for i in list_ditch.splitlines():
###            grass.run_command("v.extract",input='interfaces', layer=2, output='temp_ditch',where="cat=%s"%i,overwrite=True)
###            grass.run_command("v.to.points",input='temp_ditch',output='temp_point',flags='nt',overwrite=True)
###            puntos = grass.read_command("v.out.ascii",input='temp_point',fs=',')
###            #extract coordinates
###            a1=puntos.rsplit()
###            b1=a1[0]+'cat'
###            categ1=','+ str(i)+'cat'
###            c1=b1.replace(categ1,'')
###            b2=a1[1]+'cat'
###            categ2=','+ str(i)+'cat'
###            c2=b2.replace(categ2,'')
###            #consult height value
###            rwhat1=grass.read_command("r.what",input=rasterStr,fs=',',east_north=c1,flags='c')	
###            height_erase1=c1+',,'
###            height1=rwhat1.replace(height_erase1,'')
###            rwhat2=grass.read_command("r.what",input=rasterStr,fs=',',east_north=c2,flags='c')	
###            height_erase2=c2+',,'
###            height2=rwhat2.replace(height_erase2,'')
###            height_average= round(float(height1)/2,2)+ round(float(height2)/2,2)
###            grass.run_command("v.db.update", map='interfaces', layer=2, col='meanheight', where="cat=%s"%i, value=height_average)
###        grass.run_command("g.remove", flags='f', vect='temp_point,temp_ditch', overwrite=True)
        self.tc9.Value = ">> 1:  GRASS map 'interfaces' created."
        print(self.tc9.Value)
        
  #1.1. Calculate centers of boundaries for WTRI
  ##		grass.run_command("v.line.center",  input=HRUboundaries, output= "HRUboundaries_center",  overwrite=True)
  
  #2.Upload 'wti', 'landUse' and 'river' and 'HRUboundaries_center' tables to the postgreSql serveur
        grass.run_command("v.out.ogr", input='interfaces', type='boundary', layer=2,  dsn='PG:host='+hostStr+' dbname='+dbNameStr+' user='+userStr,  format='PostgreSQL',  \
                           olayer='wti',  overwrite=True)
        self.tc9.Value += "\n\n>> 2:  PostgreSQL database "+ dbNameStr+" updated with table 'wti'."
        grass.run_command("v.out.ogr", input=landUseStr, type='area', layer=1,  dsn='PG:host='+hostStr+' dbname='+dbNameStr+' user='+userStr,  format='PostgreSQL',  \
                           olayer='land_use')
        self.tc9.Value += "\n     > PostgreSQL database "+ dbNameStr+" updated with table 'land_use'."
        grass.run_command("v.out.ogr", input=riverStr , type='line', layer=1,  dsn='PG:host='+hostStr+' dbname='+dbNameStr+' user='+userStr,  format='PostgreSQL',  \
                           olayer='river')
        self.tc9.Value += "\n     > PostgreSQL database "+ dbNameStr+" updated with table 'river'."
##       grass.run_command("v.out.ogr", input='HRUboundaries_center', type='point', layer=1,  dsn='PG:host='+hostStr+' dbname='+dbNameStr+' user='+userStr,  format='PostgreSQL',  \
##                           olayer='temp_boundaries_center',  overwrite=True)
##        self.tc9.Value += "\n\n>> 2:  PostgreSQL database "+ dbNameStr+" updated with table 'temp_boundaries_center'."
        print(self.tc9.Value)
   #3.Removing boundaries that aren't all_interfaces interfaces
        #modifying table wti
        myconnexion.query("ALTER TABLE wti ADD COLUMN id_a integer;" +
                                        "ALTER TABLE wti ADD COLUMN id_b integer;" + 
                                        "ALTER TABLE wti ADD COLUMN centera_geom geometry;" +
                                        "ALTER TABLE wti ADD COLUMN centerb_geom geometry;" +
                                        "ALTER TABLE wti RENAME COLUMN wkb_geometry TO interf_geom;" )
        #removing non interfacing boundaries
        #myconnexion.query("DELETE FROM wti WHERE \"left\"=-1 OR \"right\"=-1;")
        self.tc9.Value += "\n\n>> 3:  PostgreSQL database "+ dbNameStr+" updated by deleting not-interfacing geometries (for all_interfaces)."
        print(self.tc9.Value)
    #4.Catching right ids and geometries of  connected polygones into 'wti' table
        myconnexion.query("UPDATE only wti "  +
                                    "SET id_a=b.\"" + polygId +"\" " +
                                    "FROM land_use AS b WHERE \"left\" = b.cat" )
        myconnexion.query("UPDATE only wti "  +
                                    "SET id_b = b.\"" + polygId +"\" " +
                                    "FROM land_use AS b WHERE \"right\" = b.cat" )
        myconnexion.query("UPDATE only wti "  +
                                    "SET centera_geom = St_centroid(b.wkb_geometry) " +
                                    "FROM land_use AS b WHERE \"left\"= b.cat" )
        myconnexion.query("UPDATE only wti "  +
                                    "SET centerb_geom = St_centroid(b.wkb_geometry) " +
                                    "FROM land_use AS b WHERE \"right\" = b.cat" )
        myconnexion.query("ALTER TABLE wti DROP COLUMN \"left\";" +
                                        "ALTER TABLE wti DROP COLUMN \"right\";" )
        myconnexion.query("ALTER TABLE wti RENAME TO all_interfaces;")
        
        self.tc9.Value += "\n\n>> 4:  PostgreSQL database "+ dbNameStr+" updated by adding polygones geometries to 'interfaces'(for all_interfaces)."
        self.tc9.Value += "\n\n>> ...DONE."
        print(self.tc9.Value)
	grass.run_command("g.remove",vect='interfaces')

	
        myconnexion.close()

#Handled method 'OnQuit'
    def OnQuit(self, event):
        self.Close()

  

##############
###      Main       ###     
##############
app = wx.App()
Win(None, -1, 'p.all_interfaces.py', (460, 650))
app.MainLoop()
