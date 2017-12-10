import FreeCAD
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

        self.CreateNewAlignment()

        return

    def IsActive (self):
        return True

    def CreateDocument (self):

        FreeCAD.newDocument("Unnamed Alignment")
        FreeCAD.setActiveDocument("Unnamed_Alignment")
        FreeCAD.ActiveDocument=FreeCAD.getDocument("Unnamed_Alignment")
        FreeCADGui.ActiveDocument=FreeCADGui.getDocument("Unnamed_Alignment")

    def CreateNewAlignment (self):

        fbs = FeedbackSketcherUtils.buildFeedbackSketch (
        sketchName = "Unnamed_Alignment", 
        clientList = ['Horizontal_Geometry', 'Vertical_Geometry'])

        #horizSketch = 


FreeCADGui.addCommand ('NewAlignment',NewAlignment()) 
