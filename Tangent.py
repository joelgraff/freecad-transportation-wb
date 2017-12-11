import FreeCADGui

class Tangent():

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon',
                'Accel' : "Shift+T",
                'MenuText': "Tangent",
                'ToolTip' : "Add a tangnet"}

    def Activated(self):
        
        #get the selected element
        #add the tangent after that element
        #apply tangential constraints to tangent and preceeding
        #unless it's true north, then add a angle constraint

        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument <> None

FreeCADGui.addCommand('Tangent',Tangent()) 
