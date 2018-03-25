# Unit test for the transportationwb.vehicle module


import FreeCAD, os, unittest, FreeCADGui, transportationwb

class VehicleTest(unittest.TestCase):

    def setUp(self):
        # setting a new document to hold the tests
        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != "TransportationTest":
                FreeCAD.newDocument("TransportationTest")
        else:
            FreeCAD.newDocument("TransportationTest")
        FreeCAD.setActiveDocument("TransportationTest")


    def testPivy(self):
        FreeCAD.Console.PrintLog ('Checking Pivy...\n')
        from pivy import coin
        c = coin.SoCube()
        FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(c)
        self.failUnless(c,"Pivy is not working properly")


    def testVehicle(self):
        FreeCAD.Console.PrintLog ('Checking createVehicle ...\n')
        FreeCAD.Console.PrintMessage ('Checking createVehicle...\n')
        import  transportationwb
        import  transportationwb.vehicle
        reload(transportationwb.vehicle)
        c=transportationwb.vehicle.createVehicle()
        self.failUnless(c,"createVehicle is not working properly")



    def tearDown(self):
        FreeCAD.closeDocument("TransportationTest")
        pass



