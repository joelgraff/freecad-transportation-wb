
import FreeCAD
import sys
import unittest


def Col1():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("transportationwb.Test_labeltools"))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("transportationwb.Test_miki"))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("transportationwb.traffic.Test_traffic"))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("transportationwb.vehicle.Test_vehicle"))
#    if (FreeCAD.GuiUp == 1):
#       suite.addTest(unittest.defaultTestLoader.loadTestsFromName("nurbswb.TestNurbsGui"))
    return suite


#def Col2():
#    suite = unittest.TestSuite()
#    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("nurbswb.TestNurbs"))
#    return suite
