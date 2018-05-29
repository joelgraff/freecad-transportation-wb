# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- label tools for geodata/transportation -
#--
#-- microelly 2018 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

'''tools to create labels and symbols in the 3D space
these methods extend the idea of the Draft.Label to special use cases'''

# pylint: disable=W0331
# pylint: disable=unused-import
# pylint: disable=invalid-name
# xpylint: disable=bare-except
# xpylint: disable=exec-used


# \cond
import FreeCAD
import FreeCADGui
Gui = FreeCADGui

import transportationwb
from transportationwb.miki_g import createMikiGui, MikiApp

import Draft
import nurbswb
# from nurbswb.sketch_to_bezier import SuperDraftLabel
from pivy import coin
# \endcond

def hideAllProps(obj,pns=None):
	if pns==None: pns=obj.PropertiesList
	for pn in pns:
		obj.setEditorMode(pn,2)

def readonlyProps(obj,pns=None):
	if pns==None: pns=obj.PropertiesList
	for pn in pns:
		try: obj.setEditorMode(pn,1)
		except: pass

def setWritableAllProps(obj,pns=None):
	if pns==None: pns=obj.PropertiesList
	for pn in pns:
		obj.setEditorMode(pn,0)



def createLatLonMarker(lat, lon):
    '''create a Label for a location given by Lat, Lon coordinates'''

    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Marker")

    try:
        origin = Gui.Selection.getSelection()[0]
    except:
        origin = None

    SuperDraftLabel(obj, mode='LatLon', origin=origin)
    print ("POSIZIOM-------------",obj.TargetPoint)

    if FreeCAD.GuiUp:
        Draft.ViewProviderDraftLabel(obj.ViewObject)

    obj.StraightDirection = 'Horizontal'
    obj.LabelType = 'Custom'
    FreeCAD.ActiveDocument.recompute()

    obj.ViewObject.TextSize = '16 mm'
    obj.ViewObject.DisplayMode = "2D text"
    obj.ViewObject.TextAlignment = "Top"

    obj.LAT = lat
    obj.LON = lon
    obj.Proxy.onChanged(obj, "XXX")

    obj.Placement = FreeCAD.Placement(obj.TargetPoint + FreeCAD.Vector(
        -100, 100, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))

    return obj


#------------------------------------------------

def createLabel(obj, ref, ctext):
    '''creates a label for the suboject ref of the object obj
    the label is connected with the coordiantes of the subobject
    '''

    l = Draft.makeLabel(
        target=(obj, ref),
        direction='Horizontal', distance=.0,
        labeltype='Custom',
    )

    l.CustomText = ctext
    l.Label = l.CustomText[0]

    com = l.Target[0].Shape.BoundBox.Center
    xmin = l.Target[0].Shape.BoundBox.XMin

    l.CustomText = ctext
    l.Label = l.CustomText[0]

    if l.Target[1][0].startswith("Edge") or l.Target[1][0].startswith("Fac"):
        pp = getattr(l.Target[0].Shape, l.Target[1][0]).CenterOfMass
        l.TargetPoint = getattr(l.Target[0].Shape, l.Target[1][0]).CenterOfMass
    else:
        pp = getattr(l.Target[0].Shape, l.Target[1][0]).Point
        l.TargetPoint = getattr(l.Target[0].Shape, l.Target[1][0]).Point

    l.Placement.Base = pp
    l.Placement.Base += (pp - com) * 1.5
    diff = (pp - com)
    if diff.x < 0:
        l.StraightDistance = 1
    else:
        l.StraightDistance = -1

    l.ViewObject.TextSize = '16 mm'
    l.ViewObject.DisplayMode = "2D text"
    l.ViewObject.TextAlignment = "Top"


def createLabels(f, e, v):
    '''creates labels for faces, edges,vertexes of selected objects
    the flags f,e,v indicate which componentes should be labeled'''

    for obj in Gui.Selection.getSelection():

        dat = []

        if v:
            for i, e in enumerate(obj.Shape.Vertexes):
                dat += [
                    ["Vertex" + str(i + 1), ["V " + str(i + 1) + " @ " + obj.Label]]]
        if e:
            for i, e in enumerate(obj.Shape.Edges):
                dat += [
                    ["Edge" + str(i + 1), ["E " + str(i + 1) + " @ " + obj.Label]]]
        if f:
            for i, e in enumerate(obj.Shape.Faces):
                dat += [
                    ["Face" + str(i + 1), ["F " + str(i + 1) + " @ " + obj.Label]]]

        for d in dat:
            createLabel(obj, d[0], d[1])


class BillBoard(object):

    '''a billboard object for the active view '''

    # \cond
    def __init__(self, layout=0):
        node = Gui.ActiveDocument.ActiveView.getSceneGraph()

        bb = coin.SoVRMLBillboard()
        b = coin.SoSphere()
        t = coin.SoTransform()
        t.translation.setValue(FreeCAD.Vector(0, 0, 10))

        mat = coin.SoMaterial()
        # mat.diffuseColor.setValue([1.,0.,1.])
        mat.emissiveColor.setValue([1., 1., 0.])

        ssa = coin.SoSeparator()
        ssa.addChild(t)
        ssa.addChild(bb)

        node.addChild(ssa)
        if layout == 0:
            vertices = [(30, 20, 0), (30, 50, 0), (0, 50, 0), (0, 0, 0), ]
        if layout == 1:
            vertices = [(30, 80, 0), (0, 80, 0), (0, 0, 0), ]
        if layout == 2:
            vertices = [(60, 80, 0), (0, 80, 0), (0, 0, 0), (60, 0, 0)]

        vc = len(vertices)
        numvertices = (vc, vc)

        myVertexProperty = coin.SoVertexProperty()
        myVertexProperty.vertex.setValues(0, vc, vertices)

        # Define the FaceSet
        myFaceSet = coin.SoFaceSet()
        myFaceSet.vertexProperty = myVertexProperty
        myFaceSet.numVertices.setValues(0, 1, numvertices)

        ss = coin.SoSeparator()
        bb.addChild(ss)

        africaSep = coin.SoSeparator()
        africaTranslate = coin.SoTranslation()
        font = coin.SoFont()
        font.size = 20
        africaText = coin.SoText2()
        africaTranslate.translation = (2., 40.0, 1.)
        # africaText.string = "AFRICA"
        africaText.string.setValues(
            ["Station", "", "Road 66", "AB - CD", "EF"])
        bb.addChild(africaSep)
        textmat = coin.SoMaterial()
        textmat.diffuseColor.setValue([0., 0., 0.])
        # mat.emissiveColor.setValue([1.,1.,0.])
        africaSep.addChild(font)
        africaSep.addChild(textmat)
        africaSep.addChild(africaTranslate)
        africaSep.addChild(africaText)

        ss.addChild(mat)
        ss.addChild(myFaceSet)
        ss.addChild(b)
        self.placement = t
        self.material = mat
        self.face = ss

        self.parentN = node
        self.billboard = ssa
        self.text = africaText

    # \endcond

    def hide(self):
        '''hide the billboard'''
        self.parentN.removeChild(self.billboard)

    def show(self):
        '''show the billboard'''
        self.parentN = Gui.ActiveDocument.ActiveView.getSceneGraph()
        self.parentN.addChild(self.billboard)

    def setColor(self, r, g, b):
        '''set the color of the billboard figure'''
        self.material.emissiveColor.setValue([r, g, b])

    def setLocation(self, pos):
        '''set the placement.base of the billboard'''
        self.placement.translation.setValue(pos)

    def setText(self, text):
        '''set the multiline text of the billboard'''
        self.text.string.setValues(text)


def createBillBoard(layout='trapez'):
    '''create a billboard with graphic layout
    layouts={'trapez':0,'triangle':1,'rectangle':2}
    '''

    layouts = {'trapez': 0, 'triangle': 1, 'rectangle': 2}

    a = BillBoard(layout=layouts[layout])
    a.hide()
    a.show()
    a.setLocation(FreeCAD.Vector(50, 50, 0))
    a.setColor(0, 1, 1)
    Gui.SendMsgToActiveView("ViewFit")

    return a

    b = BillBoard()
    # b.hide()
    b.setLocation(FreeCAD.Vector(-50, 50, 0))
    b.setColor(0, 1, 0)
    b.setText(["Example", "", "A 71", "# 45", "", "Hof", "Thal"])


import Draft




class SuperDraftLabel(Draft.DraftLabel):

	##\cond
	def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg',mode='station',origin=None):
		Draft.DraftLabel.__init__(self,obj)
		obj.TargetPoint=FreeCAD.Vector()
		
		obj.Proxy = self
		obj.addProperty("App::PropertyInteger",'polescount',).polescount=12
		obj.addProperty("App::PropertyBool",'init')
		obj.addProperty("App::PropertyEnumeration",'mode').mode=['station','LatLon','Placement']
		obj.addProperty("App::PropertyFloat",'startposition').startposition=500
		obj.addProperty("App::PropertyFloat",'endposition')
		obj.addProperty("App::PropertyString",'LAT').LAT='50.340722'
		obj.addProperty("App::PropertyString",'LON').LON='11.232647'
		obj.addProperty("App::PropertyFloat",'scale').scale=100000
		obj.addProperty("App::PropertyLink",'origin')
		
		# obj.addProperty("App::PropertyLink",'source')
		self.Type = "Label"
		obj.mode=mode
		obj.origin=origin

		if mode=='LatLon':
			hideAllProps(obj)
			pns=['Label','Placement','LAT','LON','origin','mode','TargetPoint','scale']
			setWritableAllProps(obj,pns)


	def onChanged(self, obj, prop):
	#	print ("onChange BBB", prop)
		Draft.DraftLabel.onChanged(self, obj, prop)
		try: obj.mode
		except: return 
		if obj.mode=='station':
			# stationing change if the position has changed
			if prop=='position'  or prop=='_execute_':
				obja=obj.Target[0]
				w=obja.Shape
				l=w.Length
				obj.endposition = obj.startposition + l

				pts=obja.Shape.discretize(1000)
				posa=1000/l*obj.position

				obj.TargetPoint=pts[int(round(posa))]
				obj.Label="Station "+str(obj.startposition)+" + "+str(obj.position)+ " @ " + obja.Label
				obj.CustomText=[obj.Label, "segment length: "+str(l),"street name: Baker street",
					'LAT:'+str(obj.LAT),'LON:'+str(obj.LON)]
				Draft.DraftLabel.execute(self, obj)
				return


		if  obj.mode=='LatLon': # process a lat lon marker
			if  prop in ['_execute_','LAT','LON']:

				lat=float(obj.LAT)
				lon=float(obj.LON)

				if obj.origin != None:

					latc=float(obj.origin.LAT)
					lonc=float(obj.origin.LON)

					import transversmercator
					reload(transversmercator)

					pos=transversmercator.getpos(latc,lonc,lat,lon)
					scale= obj.origin.scale
					pos /= scale 
					obj.TargetPoint=pos+obj.origin.TargetPoint

				obj.ViewObject.DisplayMode = u"2D text"
				obj.ViewObject.TextSize=16
				obj.StraightDistance = 20
				obj.CustomText=[obj.Label,str(obj.LAT),str(obj.LON)]
				obj.LabelType = u"Custom"
				Draft.DraftLabel.execute(self, obj)

		if  obj.mode=='Placement': # process a lat lon marker backward
			if  prop in ['_execute_','mode','TargetPoint']:

				print "Aendere lat lon"
				if obj.origin != None:

					x=obj.TargetPoint.x * obj.origin.scale
					y=obj.TargetPoint.y * obj.origin.scale

					latc=float(obj.origin.LAT)
					lonc=float(obj.origin.LON)

					import transversmercator
					reload(transversmercator)

					print (latc,lonc,x,y)
					print obj.origin.scale
					lat,lon=transversmercator.getlatlon(latc,lonc,x,y)
					print ("##",lat,lon)
					obj.LAT=str(lat)
					obj.LON=str(lon)


				obj.ViewObject.DisplayMode = u"2D text"
				obj.ViewObject.TextSize=16
				obj.StraightDistance = 20
				obj.CustomText=[obj.Label,str(obj.LAT),str(obj.LON)]
				obj.LabelType = u"Custom"
				Draft.DraftLabel.execute(self, obj)



	def execute(self,obj):
		try:
			self.onChanged(obj,'_execute_')
		except: 
			print ("no exe")




#
# Gui for the methods ...
#



# \cond
class GeoLocationApp(MikiApp):

    '''backend for the createGeoLocation dialog'''

    def run(self):
        createLatLonMarker(
            self.root.ids['lat'].text(),
            self.root.ids['lon'].text()
        )
# \endcond


def createGeoLocationGUI():
    '''dialog to create a Label for a location given by Lat, Lon coordinates'''

    layout = '''MainWindow:
	resize: QtCore.QSize(400,200)
	QtGui.QLabel:
		setText:"***  Create a Location object  ***"
	VerticalLayout:
		HorizontalGroup:
			setTitle: "data"
			HorizontalLayout:
				QtGui.QLabel:
					setText: "LAT"
				QtGui.QLineEdit:
					id: 'lat'
					setText:"51.12345678"
			HorizontalLayout:
				QtGui.QLabel:
					setText: "LON"
				QtGui.QLineEdit:
					id: 'lon'
					setText:"10.987654321"
		HorizontalGroup:
			setTitle: "actions"
			QtGui.QPushButton:
				setText: "run"
				clicked.connect: app.run
			QtGui.QPushButton:
				setText: "close"
				clicked.connect: app.close
	'''

    mikigui = createMikiGui(layout, GeoLocationApp)
    return mikigui


# \cond
class LabelApp(MikiApp):

    '''backend for the create All Labels dialog'''

    def run(self):
        createLabels(
            self.root.ids['faces'].isChecked(),
            self.root.ids['edges'].isChecked(),
            self.root.ids['vertexes'].isChecked()
        )
# \endcond


def createAllLabelsGUI():
    '''dialog to create labels for all components of a selected object'''

    layout = '''MainWindow:
	#resize: QtCore.QSize(400,200)
	QtGui.QLabel:
		setText:"***  Create Labels for subobjects of a selected object  ***"
	VerticalGroup:
		setTitle: "selection"
		QtGui.QCheckBox:
			id: 'faces'
			setText: 'create labels for all faces'
		QtGui.QCheckBox:
			id: 'edges'
			setText: 'create labels for all edges'
		QtGui.QCheckBox:
			id: 'vertexes'
			setText: 'create labels for all vertexes'

	HorizontalGroup:
		setTitle: "actions"
		QtGui.QPushButton:
			setText: "run"
			clicked.connect: app.run
		QtGui.QPushButton:
			setText: "close"
			clicked.connect: app.close
	'''

    mikigui = createMikiGui(layout, LabelApp)
    return mikigui


# \cond
class BillBoardApp(MikiApp):

    '''backend method for create Graphic Label dialog'''

    def run(self):
        #print self.root.ids['layout'].currentText()
        createBillBoard(self.root.ids['layout'].currentText())
# \endcond


def createGraphicLabelGUI():
    '''dialog to create a label with some graphic as a billboard'''

    layout = '''MainWindow:
	#resize: QtCore.QSize(400,200)
	QtGui.QLabel:
		setText:"***  Create Label with graphic symbols for a selected object  ***"
	VerticalGroup:
		setTitle: "selection"
		HorizontalLayout:
			QtGui.QLabel:
				setText: "Layout of the banner"
			QtGui.QComboBox:
				id: 'layout'
				addItem: "trapez"
				addItem: "triangle"
				addItem: "rectangle"

	HorizontalGroup:
		setTitle: "actions"
		QtGui.QPushButton:
			setText: "run"
			clicked.connect: app.run
		QtGui.QPushButton:
			setText: "close"
			clicked.connect: app.close
	'''

    mikigui = createMikiGui(layout, BillBoardApp)
    return mikigui


#
# StationingApp todo #+#
#

def createStationingGUI():
    '''dialog to create a stationing for a selected wire'''

    layout = '''MainWindow:
	#resize: QtCore.QSize(400,200)
	QtGui.QLabel:
		setText:"***  Create Stationing  ***"
	QtGui.QLabel:
		setText: "not implemented/merged yet"

	HorizontalGroup:
		setTitle: "actions"
		QtGui.QPushButton:
			setText: "run"
#			clicked.connect: app.run
		QtGui.QPushButton:
			setText: "close"
			clicked.connect: app.close
	'''

    mikigui = createMikiGui(layout, MikiApp)
    return mikigui
