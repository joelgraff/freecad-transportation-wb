import unittest
from Geometry import *

def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.defaultTestLoader.loadTestsFromName('transportationwb.tests.GeometryTests.test_support'))

    return suite

def execute():
    runner = unittest.TextTestRunner()
    runner.run(suite())