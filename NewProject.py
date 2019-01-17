import FreeCAD as App
import FreeCADGui as Gui
import os
from PySide import QtGui, QtCore

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

        self._set_preferences()
        return

    def IsActive(self):
        return True

    def _attach_handlers(self):
        Gui.ActiveDocument.ActiveView.addDraggable

    def _set_preferences(self):
        App.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", 7)
        App.ParamGet('User parameter:BaseApp/Preferences/Mod/Sketcher').SetBool('AutoRecompute', False)
        App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool('DuplicateLabels', True)

    def _create_document(self):

        '''
        Create a new project with default groups
        '''
        dlg = QtGui.QInputDialog()
        dlg.setWindowTitle("New Proejct")
        dlg.setLabelText('Enter project name:')
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)
        dlg.exec_()

        if dlg.result() == False:
            return

        project_name = dlg.textValue()

        if project_name =='':
            return

        App.newDocument(project_name)
        App.setActiveDocument(project_name)
        App.ActiveDocument = App.getDocument(project_name)
        Gui.ActiveDocument = Gui.getDocument(project_name)

Gui.addCommand('NewProject',NewProject())
