import FreeCAD as App
import FreeCADGui as Gui
import os

class NewProject():

    def GetResources(self):

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/workbench.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Shift+N",
                'MenuText': "New Project",
                'ToolTip' : "Create a new project document and make it active",
                'CmdType' : "ForEdit"}

    def Activated(self):

        if Gui.ActiveDocument == None:
            self._create_document()

        self._set_units()

        return

    def IsActive(self):
        return True

    def _attach_handlers(self):
        Gui.ActiveDocument.ActiveView.addDraggable

    def _set_units(self):
        App.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", 5)

    def _create_document(self):

        App.newDocument("Unnamed Project")
        App.setActiveDocument("Unnamed_Project")
        App.ActiveDocument = App.getDocument("Unnamed_Project")
        Gui.ActiveDocument = Gui.getDocument("Unnamed_Project")

Gui.addCommand('NewProject',NewProject())
