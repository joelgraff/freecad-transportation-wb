import FreeCAD
import FreeCADGui
Gui = FreeCADGui
App=FreeCAD

import time
from pivy import coin

import transportationwb
from transportationwb.miki_g import createMikiGui2, MikiApp
reload(transportationwb.miki_g)

App.closeDocument("Unnamed")
App.newDocument("Unnamed")
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")

# create the scene

layout='''#: from pivy.coin import * 
SoSeparator:
	id: 'IVRoot'
	SoSeparator:
		SoMaterial:
			emissiveColor: 0.2, 0., 0.0
		SoBaseColor:
			rgb: 1, 0 ,0
		SoRotationXYZ:
			axis:	2
			angle:1.5708
		SoTranslation:
		
			id:'pos'
			translation: 0,-40,20
		SoCylinder:
			radius: 30
			height:200

	SoSeparator:
		SoMaterial:
			emissiveColor:0, 0, .1
			transparency: 0.1
		SoBaseColor:
			rgb: 0,0,1
		SoClipPlane:
			plane: coin.SbPlane(coin.SbVec3f(0.,1.,0.),0.)
			id:'cp_blue_a'
		SoClipPlane:
			plane: coin.SbPlane(coin.SbVec3f(-1.,0.,0.),-80.)
			id:'cp_blue_b'
		SoCube:
			height: 150
			width:200
			depth:150

	SoSeparator:
		SoTranslation:
			translation: 100,10,-50
		SoClipPlane:
			id:'cp_green'
			plane: coin.SbPlane(coin.SbVec3f(-1.,0.,0.),0.)
		SoMaterial:
			emissiveColor: 0, .1, 0
			transparency: 0.2
		SoBaseColor:
			rgb: 0, 1, 0
		SoCube:
			height: 100
			width:150
			depth:100

MainWindow:
	id: 'QtRoot'
	#resize: QtCore.QSize(400,200)
	QtGui.QLabel:
		setText:"***  Clip Plane Demo Animation  ***"

	VerticalGroup:
		setTitle: "actions"
		QtGui.QPushButton:
			id: "run"
			setText: "list all ids"
			clicked.connect: app.run
		QtGui.QPushButton:
			setText: "run green clipplane animation"
			clicked.connect: app.run_green
		QtGui.QPushButton:
			setText: "run blue clipplane animation A"
			clicked.connect: app.run_blue_a
		QtGui.QPushButton:
			setText: "run blue clipplane animation B"
			clicked.connect: app.run_blue_b

		QtGui.QPushButton:
			setText: "activate all clip planes"
			clicked.connect: app.activate_all

		QtGui.QPushButton:
			setText: "deactivate all clip planes"
			clicked.connect: app.deactivate_all

		QtGui.QPushButton:
			setText: "reset all clip planes"
			clicked.connect: app.reset_planes

		QtGui.QPushButton:
			setText: "close"
			clicked.connect: app.close

'''

class ComboApp(MikiApp):

	def close(self):
		s=self.root.ids['IVRoot']
		sg=Gui.ActiveDocument.ActiveView.getSceneGraph()
		sg.removeChild(s)
		s=self.root.ids['QtRoot']
		s.hide()

	def run(self):
		for mid in self.root.ids:
			print mid

	def run_green(self):
		'''run animation green'''
		ids=self.root.ids
		for i in range(-40,14):
			ids['cp_green'].plane.setValue(coin.SbPlane(coin.SbVec3f(-1.,0.,0.),i*5))
			Gui.updateGui()
			time.sleep(0.01)

	def run_blue_b(self):
		'''run animation'''
		ids=self.root.ids
		for i in range(-70,10):
			ids['cp_blue_b'].plane.setValue(coin.SbPlane(coin.SbVec3f(-1.,0.,0.),i*2))
			Gui.updateGui()
			time.sleep(0.01)

	def run_blue_a(self):
		'''run animation'''
		ids=self.root.ids
		for i in range(-40,20):
			ids['cp_blue_a'].plane.setValue(coin.SbPlane(coin.SbVec3f(0.,1.,0.),i*2))
			Gui.updateGui()
			time.sleep(0.01)

	def activate_all(self):

		ids=self.root.ids
		ids['cp_blue_a'].on.setValue(1)
		ids['cp_blue_b'].on.setValue(1)
		ids['cp_green'].on.setValue(1)

	def reset_planes(self):
		ids=self.root.ids
		ids['cp_green'].plane.setValue(coin.SbPlane(coin.SbVec3f(-1.,0.,0.),-200))
		ids['cp_blue_b'].plane.setValue(coin.SbPlane(coin.SbVec3f(-1.,0.,0.),-140))
		ids['cp_blue_a'].plane.setValue(coin.SbPlane(coin.SbVec3f(0.,1.,0.),-80))

	def deactivate_all(self):

		ids=self.root.ids
		ids['cp_blue_a'].on.setValue(0)
		ids['cp_blue_b'].on.setValue(0)
		ids['cp_green'].on.setValue(0)


def demoClipPlaneAnimationGUI():
	(node,miki) = createMikiGui2(layout, ComboApp)
	Gui.activeDocument().activeView().viewAxonometric()
	Gui.updateGui()
	Gui.SendMsgToActiveView("ViewFit")

