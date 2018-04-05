# Unit test for the transportationwb.vehicle module


import FreeCAD, os, unittest, FreeCADGui #, transportationwb

class MikiTestU(unittest.TestCase):

	def setUp(self):
		# setting a new document to hold the tests
		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTestA")
		else:
			FreeCAD.newDocument("TransportationTestA")
		FreeCAD.setActiveDocument("TransportationTestA")


	def testMiki(self):
		FreeCAD.Console.PrintMessage('!-! Checking miki...\n')
		import  transportationwb
		import  transportationwb.miki_g
		reload(transportationwb.miki_g)
		FreeCAD.Console.PrintMessage('!####! Checking miki...\n')

		c=transportationwb.miki_g.testme()
		FreeCAD.Console.PrintMessage('Checking miki...\n' + str(c)+"\n")
		self.failUnless(c<>None,"Miki is not working properly")

		c=transportationwb.miki_g.testDialogTab()
		FreeCAD.Console.PrintMessage('Checking miki...\n' + str(c)+"\n")
		self.failUnless(c<>None,"Miki is not working properly")

		c=transportationwb.miki_g.testDialogMainWindow()
		FreeCAD.Console.PrintMessage('Checking miki...\n' + str(c)+"\n")
		self.failUnless(c<>None,"Miki is not working properly")

		c=transportationwb.miki_g.testDialogDockWidget()
		FreeCAD.Console.PrintMessage('Checking miki...\n' + str(c)+"\n")
		self.failUnless(c<>None,"Miki is not working properly")


	def tearDown(self):
		# FreeCAD.closeDocument("TransportationTestA")
		pass



