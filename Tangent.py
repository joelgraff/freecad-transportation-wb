import FreeCADGui

class Tangent():
    """Tangent"""

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon', # the name of a svg file available in the resources
                'Accel' : "Shift+T", # a default shortcut (optional)
                'MenuText': "Tangent",
                'ToolTip' : "Add a tangnet"}

    def Activated(self):
        "Do something here"
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument <> None

FreeCADGui.addCommand('Tangent',Tangent()) 
