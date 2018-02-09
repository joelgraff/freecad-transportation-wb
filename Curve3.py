import FreeCADGui

class Curve3():
    """Curve3"""

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon', # the name of a svg file available in the resources
                'Accel' : "Shift+3", # a default shortcut (optional)
                'MenuText': "Three-Center Curve",
                'ToolTip' : "Add a three-center curve"}

    def Activated(self):
        "Do something here"
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument != None

FreeCADGui.addCommand('Curve3',Curve3()) 
