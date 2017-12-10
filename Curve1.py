import FreeCADGui

class Curve1():
    """Curve1"""

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon', # the name of a svg file available in the resources
                'Accel' : "Shift+1", # a default shortcut (optional)
                'MenuText': "One-Center Curve",
                'ToolTip' : "Add a one-center curve"}

    def Activated(self):
        "Do something here"
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument <> None

FreeCADGui.addCommand('Curve1',Curve1()) 
