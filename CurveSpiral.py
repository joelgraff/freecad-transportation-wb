import FreeCADGui

class CurveSpiral():
    """CurveSpiral"""

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon', # the name of a svg file available in the resources
                'Accel'   : "Shift+S", # a default shortcut (optional)
                'MenuText': "Spiral Curve",
                'ToolTip' : "Add a spiral curve"}

    def Activated(self):
        "Do something here"
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument <> None

FreeCADGui.addCommand('CurveSpiral',CurveSpiral())
