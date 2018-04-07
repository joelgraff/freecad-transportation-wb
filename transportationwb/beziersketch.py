# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- bezier sketch
#--
#-- microelly 2018 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
'''create bezier curves in sketcher'''
##\cond

# from say import *
# import nurbswb.pyob
#------------------------------
import FreeCAD,FreeCADGui,Sketcher,Part

App = FreeCAD
Gui = FreeCADGui

from PySide import QtCore


import numpy as np
import time
import random

class FeaturePython:
	''' basic defs'''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


class ViewProvider:
	''' basic defs '''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


	def setupContextMenu(self, obj, menu):
		menu.clear()
		action = menu.addAction("MyMethod #1")
		action.triggered.connect(lambda:self.methodA(obj.Object))
		action = menu.addAction("MyMethod #2")
		menu.addSeparator()
		action.triggered.connect(lambda:self.methodB(obj.Object))
		action = menu.addAction("Edit Sketch")
		action.triggered.connect(lambda:self.myedit(obj.Object))


	def myedit(self,obj):
		self.methodB(None)
		Gui.activeDocument().setEdit(obj.Name)
		self.methodA(None)

	def methodA(self,obj):
		print "my Method A"
		FreeCAD.activeDocument().recompute()

	def methodB(self,obj):
		print "my method B"
		FreeCAD.activeDocument().recompute()

	def methodC(self,obj):
		print "my method C"
		FreeCAD.activeDocument().recompute()

	def unsetEdit(self,vobj,mode=0):
		self.methodC(None)


	def doubleClicked(self,vobj):
		print "double clicked"
		self.myedit(vobj.Object)
		print "Ende double clicked"


def getNamedConstraint(sketch,name):
	'''get the index of a constraint name'''
	for i,c in enumerate (sketch.Constraints):
		if c.Name==name: return i
	print ('Constraint name "'+name+'" not in ' +sketch.Label)
	raise Exception ('Constraint name "'+name+'" not in ' + sketch.Label)



def clearReportView(name):
	from PySide import QtGui
	mw=Gui.getMainWindow()
	r=mw.findChild(QtGui.QTextEdit, "Report view")
	r.clear()
	import time
	now = time.ctime(int(time.time()))
	App.Console.PrintWarning("Cleared Report view " +str(now)+" by " + name+"\n")
##\endcond


class BezierSketch(FeaturePython):
	'''Sketch Object with Python for Bezier Curve''' 

	##\cond
	def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj
		self.aa = None
#		obj.addProperty("App::PropertyBool",'clearReportview', 'Base',"clear window for every execute")

		obj.addProperty("App::PropertyBool",'simple', )
		obj.addProperty("App::PropertyBool",'aTangential',)
		obj.addProperty("App::PropertyBool",'bTangential',)
		obj.addProperty("App::PropertyLink",'aSketch', )
		obj.addProperty("App::PropertyLink",'bSketch', )
		ViewProvider(obj.ViewObject)
		
		obj.aTangential=True
		obj.bTangential=True
		
	##\endcond


	def execute(proxy,obj):
		'''sync connection aSketch and bSketch'''

		print "myExecute ..."
		if not obj.simple:
			if obj.aSketch <>None:
				print obj.aSketch
				print obj.aSketch.getDatum('Ax')
				obj.setDriving(26,True)
				obj.setDatum('Ax',obj.aSketch.getDatum('Bx'))
				obj.setDriving(27,True)
				obj.setDatum('Ay',obj.aSketch.getDatum('By'))
				obj.setDriving(30,True)
				obj.setDatum('Aarc',(180+obj.aSketch.getDatum('Barc').Value)*np.pi/180)
				
			else:
				obj.setDriving(26,False)
				obj.setDriving(27,False)
				obj.setDriving(30,False)

			if obj.bSketch <>None:
				print obj.aSketch
				print obj.aSketch.getDatum('Ax')
				obj.setDriving(28,True)
				obj.setDatum('Bx',obj.bSketch.getDatum('Ax'))
				obj.setDriving(29,True)
				obj.setDatum('By',obj.bSketch.getDatum('Ay'))
				obj.setDriving(31,True)
				obj.setDatum('Barc',(180+obj.bSketch.getDatum('Aarc').Value)*np.pi/180)

			else:
				obj.setDriving(28,False)
				obj.setDriving(29,False)
				obj.setDriving(31,False)
		else:
			if obj.aSketch <>None:
				print obj.aSketch
				print obj.aSketch.getDatum('Ax')
				obj.setDriving(14,True)
				obj.setDatum('Ax',obj.aSketch.getDatum('Bx'))
				obj.setDriving(15,True)
				obj.setDatum('Ay',obj.aSketch.getDatum('By'))
				obj.setDriving(18,True)
				obj.setDatum('Aarc',(180+obj.aSketch.getDatum('Barc').Value)*np.pi/180)
				
			else:
				obj.setDriving(14,False)
				obj.setDriving(15,False)
				obj.setDriving(18,False)

			if obj.bSketch <>None:
				print obj.aSketch
				print obj.aSketch.getDatum('Ax')
				obj.setDriving(16,True)
				obj.setDatum('Bx',obj.bSketch.getDatum('Ax'))
				obj.setDriving(17,True)
				obj.setDatum('By',obj.bSketch.getDatum('Ay'))
				obj.setDriving(19,True)
				obj.setDatum('Barc',(180+obj.bSketch.getDatum('Aarc').Value)*np.pi/180)

			else:
				obj.setDriving(16,False)
				obj.setDriving(17,False)
				obj.setDriving(19,False)

		obj.recompute()
		return




#	def onChanged(self, obj, prop):
#		print ("onChange", prop)
#		return



def createbezier(sk):
	'''create a curve segment with 7 poles'''


	pts=[
			(0,0,0),(0,-100,0),
			(200,0,0),(300,0,0),(400,0,0),
			(600,-100,0),(600,0,0)
		]

	pts2=[FreeCAD.Vector(p) for p in pts]
	pts=pts2


	sk.addGeometry(Part.Circle(pts[0],App.Vector(0,0,1),10),True)
	sk.addConstraint(Sketcher.Constraint('Radius',0,10.000000)) 

	for i in range(1,7):
		sk.addGeometry(Part.Circle(pts[i],App.Vector(0,0,1),10),True)
		sk.addConstraint(Sketcher.Constraint('Equal',0,i)) 

	sk.addGeometry(Part.BSplineCurve(pts,None,None,False,3,None,False),False)

	conList = []
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',0,3,7,0))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',1,3,7,1))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',2,3,7,2))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',3,3,7,3))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',4,3,7,4))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',5,3,7,5))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',6,3,7,6))

	sk.addConstraint(conList)
	sk.exposeInternalGeometry(7)

	App.ActiveDocument.recompute()

	sk.addGeometry(Part.LineSegment(pts[2],pts[4]),True)
	sk.addConstraint(Sketcher.Constraint('Coincident',13,1,2,3)) 
	sk.addConstraint(Sketcher.Constraint('Coincident',13,2,4,3)) 
	App.ActiveDocument.recompute()
	sk.addConstraint(Sketcher.Constraint('PointOnObject',3,3,13)) 

	sk.addGeometry(Part.LineSegment(pts[-1],pts[-2]),True)

	sk.addConstraint(Sketcher.Constraint('Coincident',14,1,6,3)) 
	sk.addConstraint(Sketcher.Constraint('Coincident',14,2,5,3)) 
	App.ActiveDocument.recompute()

	sk.addGeometry(Part.LineSegment(pts[0],pts[1]),True)

	sk.addConstraint(Sketcher.Constraint('Coincident',15,1,0,3)) 
	sk.addConstraint(Sketcher.Constraint('Coincident',15,2,1,3)) 
	App.ActiveDocument.recompute()

	sk.addConstraint(Sketcher.Constraint('DistanceX',0,3,0)) 
	sk.addConstraint(Sketcher.Constraint('DistanceY',0,3,0)) 
	App.ActiveDocument.recompute()
	sk.renameConstraint(26, u'Ax')
	App.ActiveDocument.recompute()
	sk.renameConstraint(27, u'Ay')
	sk.addConstraint(Sketcher.Constraint('DistanceX',6,3,600)) 
	sk.addConstraint(Sketcher.Constraint('DistanceY',6,3,000)) 
	App.ActiveDocument.recompute()
	sk.renameConstraint(28, u'Bx')
	sk.renameConstraint(29, u'By')

	sk.addConstraint(Sketcher.Constraint('Angle',15,2,-1,2,0.5*np.pi)) 
	sk.renameConstraint(30, u'Aarc')
	sk.addConstraint(Sketcher.Constraint('Angle',14,2,-1,2,-0.5*np.pi)) 
	sk.renameConstraint(31, u'Barc')
	App.activeDocument().recompute()
	for i in range(26,32):
		sk.setDriving(i,False)

	for i in range(32):
		sk.toggleVirtualSpace(i)

	sk.addConstraint(Sketcher.Constraint('Symmetric',2,3,4,3,3,3)) 
	cc=sk.addGeometry(Part.Circle(App.Vector(600.,0.0,0),App.Vector(0,0,1),20.),False)
	sk.addConstraint(Sketcher.Constraint('Coincident',cc,3,6,3)) 

	App.ActiveDocument.recompute()



def createsimplebezier(sk):
	'''create a simple bezier curve with 4 poles'''

	pts=[
			(0,0,0),(0,-100,0),
			(600,-100,0),(600,0,0)
		]


	pts2=[FreeCAD.Vector(p) for p in pts]
	pts=pts2

	sk.addGeometry(Part.Circle(pts[0],App.Vector(0,0,1),10),True)
	sk.addConstraint(Sketcher.Constraint('Radius',0,10.000000)) 

	for i in range(1,4):
		sk.addGeometry(Part.Circle(pts[i],App.Vector(0,0,1),10),True)
		sk.addConstraint(Sketcher.Constraint('Equal',0,i)) 

	bc=sk.addGeometry(Part.BSplineCurve(pts,None,None,False,3,None,False),False)

	conList = []
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',0,3,bc,0))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',1,3,bc,1))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',2,3,bc,2))
	conList.append(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint',3,3,bc,3))

	sk.addConstraint(conList)
	sk.exposeInternalGeometry(4)

	App.ActiveDocument.recompute()

	l=sk.addGeometry(Part.LineSegment(pts[-1],pts[-2]),True)

	sk.addConstraint(Sketcher.Constraint('Coincident',l,1,3,3)) 
	sk.addConstraint(Sketcher.Constraint('Coincident',l,2,2,3)) 
	App.ActiveDocument.recompute()

	l2=sk.addGeometry(Part.LineSegment(pts[0],pts[1]),True)

	sk.addConstraint(Sketcher.Constraint('Coincident',l2,1,0,3)) 
	sk.addConstraint(Sketcher.Constraint('Coincident',l2,2,1,3)) 
	App.ActiveDocument.recompute()

	sk.addConstraint(Sketcher.Constraint('DistanceX',0,3,0)) 
	sk.addConstraint(Sketcher.Constraint('DistanceY',0,3,0)) 
	App.ActiveDocument.recompute()
	
	sk.renameConstraint(14, u'Ax')
	App.ActiveDocument.recompute()
	sk.renameConstraint(15, u'Ay')
	sk.addConstraint(Sketcher.Constraint('DistanceX',3,3,600)) 
	sk.addConstraint(Sketcher.Constraint('DistanceY',3,3,0)) 
	App.ActiveDocument.recompute()
	sk.renameConstraint(16, u'Bx')
	sk.renameConstraint(17, u'By')

	sk.addConstraint(Sketcher.Constraint('Angle',l2,2,-1,2,0.5*np.pi)) 
	sk.renameConstraint(18, u'Aarc')
	sk.addConstraint(Sketcher.Constraint('Angle',l,2,-1,2,-0.5*np.pi)) 
	sk.renameConstraint(19, u'Barc')
	App.activeDocument().recompute()

	for i in range(14,20):
		sk.setDriving(i,False)

	for i in range(20):
		sk.toggleVirtualSpace(i)

	cc=sk.addGeometry(Part.Circle(App.Vector(600.000000,0.000000,0),App.Vector(0,0,1),20.),False)
	sk.addConstraint(Sketcher.Constraint('Coincident',cc,3,3,3)) 


def createBezierSketch(name="MyBezierSketch"):
	'''create a Bezier Sketch'''


	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	BezierSketch(obj)
	createbezier(obj)
	obj.ViewObject.LineColor=(random.random(),random.random(),random.random(),)
	return obj

def createSimpleBezierSketch(name="MySimpleBezierSketch"):
	'''create a Sketch for a simple bezier curve'''


	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	BezierSketch(obj)
	obj.simple=True
	createsimplebezier(obj)
	obj.ViewObject.LineColor=(random.random(),random.random(),random.random(),)
	return obj




if __name__ == '__main__':

	pass
