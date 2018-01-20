import FreeCAD
import FreeCADGui
import GeometryUtilities
from PySide import QtGui

class Tangent():

    def __init__(self):
        self.activeObject = FreeCAD.ActiveDocument.ActiveObject
            
    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon',
                'Accel' : "Shift+T",
                'MenuText': "Tangent",
                'ToolTip' : "Add a tangnet"}

    def Activated(self):

        #validate the selection, returning if invalid
        selectedGeometry = self._getSelection()

        if (selectedGeometry == None):
            QtGui.QMessageBox.critical (
                None, "Add Tangent Error", \
                "No more than one element may be selected.")
            return

        
        #create the new geometry
        newGeometry = Part.LineSegment (
            FreeCAD.Vector (0.0, 0.0), FreeCAD.Vector (1.0, 1.0))

        #insert the geometry
        #unless it's true north, then add a angle constraint

        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument <> None

#FreeCADGui.addCommand('Tangent',Tangent()) 
