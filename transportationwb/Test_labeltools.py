# Unit test for the transportationwb.labeltools module


import FreeCAD
import unittest

# pylint: disable=invalid-name


class LabeltoolsTest(unittest.TestCase):

    def setUp(self):

        import transportationwb
        import transportationwb.labeltools
        reload(transportationwb.labeltools)

        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != "TransportationTest":
                FreeCAD.newDocument("TransportationTest")
        else:
            FreeCAD.newDocument("TransportationTest")
        FreeCAD.setActiveDocument("TransportationTest")
        self.windows = []

    def testLabelGUI(self):

        if 1:
            import transportationwb.labeltools

            c = transportationwb.labeltools.createStationingGUI()
            self.windows += [c]

            c = transportationwb.labeltools.createAllLabelsGUI()
            self.windows += [c]

            c = transportationwb.labeltools.createGeoLocationGUI()
            self.windows += [c]

            c = transportationwb.labeltools.createGraphicLabelGUI()
            self.windows += [c]

    def testLabelcmds(self):

        import transportationwb.labeltools

        c = transportationwb.labeltools.createBillBoard()
        assert c

        c = transportationwb.labeltools.createLatLonMarker('51.34', '12.56')
        assert c

    def testFail(self):
        a = 1 / 0
        assert a

    def tearDown(self):
        FreeCAD.closeDocument("TransportationTest")
        for c in self.windows:
            c.hide()
