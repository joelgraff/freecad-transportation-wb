import FreeCAD
import FreeCADGui as Gui
import unittest


class beziersketch_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_getNamedConstraint(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		sk=transportationwb.beziersketch.createSimpleBezierSketch(name="MySimpleBezierSketch")
		rc=transportationwb.beziersketch.getNamedConstraint(sk,'Ax')


	def test_clearReportView(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.clearReportView('name')

'''
	def test_combineSketches(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.combineSketches()

	def test_createbezier(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.createbezier(sk)

	def test_createsimplebezier(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.createsimplebezier(sk)

	def test_ArcSplineSketch(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.ArcSplineSketch(sk)

	def test_createArcSpline(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.createArcSpline(name="Arc")

	def test_createBezierSketch(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.createBezierSketch(name="MyBezierSketch")

	def test_createSimpleBezierSketch(self):

		import transportationwb.beziersketch
		reload (transportationwb.beziersketch)
		rc=transportationwb.beziersketch.createSimpleBezierSketch(name="MySimpleBezierSketch")


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

class bogen_zeichnen_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_run(self):

		import transportationwb.bogen_zeichnen
		reload (transportationwb.bogen_zeichnen)
		rc=transportationwb.bogen_zeichnen.run(ag,ap,bg,bp,f=False )


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

class clipplane_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_demoClipPlaneAnimation(self):

		import transportationwb.clipplane
		reload (transportationwb.clipplane)
		rc=transportationwb.clipplane.demoClipPlaneAnimation()


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

class create_circle_sketch_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

class docu_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

class gentests_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_run(self):

		import transportationwb.gentests
		reload (transportationwb.gentests)
		rc=transportationwb.gentests.run(out,fn)

	def test_runall(self):

		import transportationwb.gentests
		reload (transportationwb.gentests)
		rc=transportationwb.gentests.runall(fns)


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

class geodesic_lines_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_hideAllProps(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.hideAllProps(obj,pns=None)

	def test_readonlyProps(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.readonlyProps(obj,pns=None)

	def test_setWritableAllProps(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.setWritableAllProps(obj,pns=None)

	def test_createGeodesicA(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createGeodesicA(obj=None)

	def test_createPatch(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createPatch(obj=None,wire=None)

	def test_createCurvature(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createCurvature(obj=None)

	def test_colorPath(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.colorPath(pts,color='0 1 0',name=None)

	def test_genRibForGeodesic(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.genRibForGeodesic(fp,u,v,d,lang,ribflag,color='0 1 1')

	def test_getface_old(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.getface_old(count=10)

	def test_drawColorLines(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.drawColorLines(fp,name,ivs)

	def test_updateGeodesic(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.updateGeodesic(fp)

	def test_updatePatch_old(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.updatePatch_old(fp)

	def test_updateCurvaturePath(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.updateCurvaturePath(fp,redirect,flip)

	def test_updateCurvature(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.updateCurvature(fp)

	def test_runtest1(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.runtest1()

	def test_createGeodesic(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createGeodesic()

	def test_geodesicMapPatchToFace(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.geodesicMapPatchToFace()

	def test_appendGeodesic(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.appendGeodesic()

	def test_createCurvatureStar(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createCurvatureStar()

	def test_creategeodesicbunch(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.creategeodesicbunch()

	def test_wireToPolygon(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.wireToPolygon(w)

	def test_updatePatch(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.updatePatch(fp)

	def test_approx_step(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.approx_step()

	def test_approx_geodesic(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.approx_geodesic(n=10)

	def test_genRibForUpdateDistance(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.genRibForUpdateDistance(f,u=50,v=50,d=0,lang=30,gridsize=20)

	def test_genrib_outdated(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.genrib_outdated(f,u=50,v=50,d=0,lang=30,gridsize=20)

	def test_updateDistance(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.updateDistance(fp)

	def test_geodesicDistance(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.geodesicDistance()

	def test_makeLabel(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.makeLabel(targetpoint=None,target=None,direction=None,distance=None,labeltype=None,placement=None)

	def test_createMarker(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createMarker(u=20,v=50)

	def test_findGeodesicToTarget(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.findGeodesicToTarget(start=None,target=None,d=10)

	def test_createShoeMarkers(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.createShoeMarkers()

	def test_connectMarkers(self):

		import transportationwb.geodesic_lines
		reload (transportationwb.geodesic_lines)
		rc=transportationwb.geodesic_lines.connectMarkers()


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

'''
class labeltools_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_hideAllProps(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		import Draft
		obj = Draft.makeText(["aaa","bbb"],point=FreeCAD.Vector(-121.457015991,83.2205505371,0.0))
		rc=transportationwb.labeltools.hideAllProps(obj,pns=None)

	def test_readonlyProps(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		import Draft
		obj = Draft.makeText(["aaa","bbb"],point=FreeCAD.Vector(-121.457015991,83.2205505371,0.0))
		rc=transportationwb.labeltools.readonlyProps(obj,pns=None)

	def test_setWritableAllProps(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		import Draft
		obj = Draft.makeText(["aaa","bbb"],point=FreeCAD.Vector(-121.457015991,83.2205505371,0.0))
		rc=transportationwb.labeltools.setWritableAllProps(obj,pns=None)

	def test_createLatLonMarker(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		
		rc=transportationwb.labeltools.createLatLonMarker('51','10')

	def test_createLabel(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		obj = FreeCAD.ActiveDocument.addObject("Part::Cylinder","Cylinder")
		rc=transportationwb.labeltools.createLabel(obj, 'Edge1', 'ctext')

	def test_createLabels(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		rc=transportationwb.labeltools.createLabels(1, 1, 1)

	def test_createBillBoard(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		rc=transportationwb.labeltools.createBillBoard(layout='trapez')

	def test_createGeoLocationGUI(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		rc=transportationwb.labeltools.createGeoLocationGUI()

	def test_createAllLabelsGUI(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		rc=transportationwb.labeltools.createAllLabelsGUI()

	def test_createGraphicLabelGUI(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		rc=transportationwb.labeltools.createGraphicLabelGUI()

	def test_createStationingGUI(self):

		import transportationwb.labeltools
		reload (transportationwb.labeltools)
		rc=transportationwb.labeltools.createStationingGUI()


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

'''
class miki_g_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_getMainWindow(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.getMainWindow()

	def test_getComboView(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.getComboView(mw)

	def test_ComboViewShowWidget(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.ComboViewShowWidget(widget, tabMode=False)

	def test_creatorFunction(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.creatorFunction(name)

	def test_VerticalLayoutTab(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.VerticalLayoutTab(title='')

	def test_setSpacer(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.setSpacer()

	def test_run_magic(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.run_magic(p,c)

	def test_DockWidget(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.DockWidget(title='')

	def test_MainWindow(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.MainWindow(title='')

	def test_HorizontalLayout(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.HorizontalLayout(title='')

	def test_VerticalLayout(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.VerticalLayout(title='')

	def test_HorizontalGroup(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.HorizontalGroup(title='')

	def test_VerticalGroup(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.VerticalGroup(title='')

	def test_ftab2(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.ftab2(name="horizontal")

	def test_getMainWindowByName(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.getMainWindowByName(name)

	def test_getdockwindowMgr2(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.getdockwindowMgr2(dockwindow, winname="FreeCAD")

	def test_createMikiGui(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.createMikiGui(layout, app)

	def test_createMikiGui2(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.createMikiGui2(layout, app)

	def test_testme(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.testme(mode='')

	def test_testDialogMainWindow(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.testDialogMainWindow()

	def test_testDialogTab(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.testDialogTab()

	def test_testDialogDockWidget(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.testDialogDockWidget()

	def test_testDialog(self):

		import transportationwb.miki_g
		reload (transportationwb.miki_g)
		rc=transportationwb.miki_g.testDialog()


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")
'''

class say_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_log(self):

		import transportationwb.say
		reload (transportationwb.say)
		rc=transportationwb.say.log('logs')

	def test_sayd(self):

		import transportationwb.say
		reload (transportationwb.say)
		rc=transportationwb.say.sayd('sads')

	def test_say(self):

		import transportationwb.say
		reload (transportationwb.say)
		rc=transportationwb.say.say('says')

	def test_sayErr(self):

		import transportationwb.say
		reload (transportationwb.say)
		rc=transportationwb.say.sayErr('sayerr')

	def test_sayW(self):

		import transportationwb.say
		reload (transportationwb.say)
		rc=transportationwb.say.sayW('saywarn')

	def test_errorDialog(self):

		import transportationwb.say
		reload (transportationwb.say)
		pass # ignore because its a blocking dialog 
		# rc=transportationwb.say.errorDialog('msg')

	def test_sayexc(self):

		import transportationwb.say
		reload (transportationwb.say)
		rc=transportationwb.say.sayexc(mess='')


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")


class stationing_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_combineCurves(self):

		import transportationwb.stationing
		reload (transportationwb.stationing)
		import Draft
		points = [FreeCAD.Vector(-161.653823853,-61.6617736816,0.0),FreeCAD.Vector(-64.9948348999,115.361206055,0.0),FreeCAD.Vector(118.323936462,49.0701789856,0.0),FreeCAD.Vector(185.355651855,100.547576904,0.0)]
		splineA = Draft.makeBSpline(points,closed=False,face=True,support=None)
		points = [FreeCAD.Vector(-76.8457336426,-73.8830184937,0.0),FreeCAD.Vector(-16.4801673889,6.11061906815,0.0),FreeCAD.Vector(169.060638428,-9.44369029999,0.0),FreeCAD.Vector(206.835449219,46.1074523926,0.0)]
		splineB = Draft.makeBSpline(points,closed=False,face=True,support=None)
		Gui.Selection.addSelection(splineA)
		Gui.Selection.addSelection(splineB)
		rc=transportationwb.stationing.combineCurves()


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")


class transversmercator_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

	def test_getpos(self):

		import transportationwb.transversmercator
		reload (transportationwb.transversmercator)
		rc=transportationwb.transversmercator.getpos(50,10,51,10)
		assert rc==FreeCAD.Vector (0.0, 111319490.79327373, 0.0)

	def test_getlatlon(self):

		import transportationwb.transversmercator
		reload (transportationwb.transversmercator)
		rc=transportationwb.transversmercator.getlatlon(51,10,100,100)
		assert rc==(51.000000898315264, 10.000001427437144)


	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")

