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
                'ToolTip' : "Create a new alignment and make it active"}

    def Activated (self):

        if FreeCADGui.ActiveDocument == None:
            self.CreateDocument()

        self.CreateSketches()

        self.AddTrueNorth()

        return

    def IsActive (self):
        return True

    def CreateDocument (self):

        FreeCAD.newDocument("Unnamed Alignment")
        FreeCAD.setActiveDocument("Unnamed_Alignment")
        FreeCAD.ActiveDocument=FreeCAD.getDocument("Unnamed_Alignment")
        FreeCADGui.ActiveDocument=FreeCADGui.getDocument("Unnamed_Alignment")

    def CreateSketches (self):

        fbs = FeedbackSketcherUtils.buildFeedbackSketch (
        sketchName = "Unnamed_Alignment", 
        clientList = ['Horizontal_Geometry', 'Vertical_Geometry'])

    def AddTrueNorth (self):

        sketch = FreeCAD.ActiveDocument.Horizontal_Geometry

        sketch.addGeometry (Part.LineSegment (
            FreeCAD.Vector (0.0, 0.0), FreeCAD.Vector (0.0, 1.0)))

        sketch.addConstraint (Sketcher.Constraint ("Vertical", 0))

        FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand ('NewAlignment',NewAlignment()) 
