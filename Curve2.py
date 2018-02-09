import FreeCADGui

class Curve2():
    """Curve2"""

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon', # the name of a svg file available in the resources
                'Accel' : "Shift+2", # a default shortcut (optional)
                'MenuText': "Two-Center Curve",
                'ToolTip' : "Add a two-center curve"}

    def Activated(self):
        "Do something here"
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument != None

FreeCADGui.addCommand('Curve2',Curve2()) 
