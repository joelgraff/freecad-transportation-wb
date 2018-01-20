import Sketcher
import FreeCAD
import Part
import FreeCADGui
import feedbacksketch
import FeedbackSketcherUtils
class NewAlignment():

    def GetResources (self):
        return {'Pixmap'  : 'My_Command_Icon',
                'Accel' : "Shift+N",
                'MenuText': "New Alignment",
                'ToolTip' : "Create a new alignment and make it active",
                'CmdType' : "ForEdit"}

    def Activated (self):

        if FreeCADGui.ActiveDocument == None:
            self._CreateDocument()

        self._CreateSketches()

        self._AddTrueNorth()

        return

    def IsActive (self):
        return True

    def _CreateDocument (self):

        FreeCAD.newDocument("Unnamed Alignment")
        FreeCAD.setActiveDocument("Unnamed_Alignment")
        FreeCAD.ActiveDocument=FreeCAD.getDocument("Unnamed_Alignment")
        FreeCADGui.ActiveDocument=FreeCADGui.getDocument("Unnamed_Alignment")

    def _CreateSketches (self):

        fbs = FeedbackSketcherUtils.buildFeedbackSketch (
        sketchName = "Unnamed_Alignment",
        clientList = ['Horizontal_Geometry', 'Vertical_Geometry'])

    def _AddTrueNorth (self):

        sketch = FreeCAD.ActiveDocument.Horizontal_Geometry

        trueNorth = Part.LineSegment (
            FreeCAD.Vector (0.0, 0.0), FreeCAD.Vector (0.0, 1.0))

        sketch.addGeometry (trueNorth)
        sketch.addConstraint (Sketcher.Constraint ("Vertical", 0))

        FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand ('NewAlignment',NewAlignment())
