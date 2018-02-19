from PySide import QtGui
import FreeCADGui as Gui
import CurveUtilities as CurveUtils
import os

class Curve2():
    """
    Curve2 generates a tw0-center curve.  User is required to select two adjacent backtangents for correct curve placement.
    """

    def GetResources(self):

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/two_center_curve.svg"

        return {'Pixmap'  : 'My_Command_Icon', # the name of a svg file available in the resources
                'Accel' : "Shift+2", # a default shortcut (optional)
                'MenuText': "Two-Center Curve",
                'ToolTip' : "Add a two-center curve"}

    def Activated(self):

        if Gui.Selection.getSelection() == []:
            self._notify_error("Selection")

        self.sketch = Gui.Selection.getSelection()[0]

        #abort if two adjacent back tangents are not selected
        back_tangents = CurveUtils.validate_selection(self.sketch)

        if back_tangents is None:
            return

        #build two arcs which connect in the middle.  The greater arc
        #should be 3/8 the length of the shorter back tangent.  The lesser
        #arc should be 3/4 the length of the greather arc.
        return

    def IsActive(self):
        return Gui.ActiveDocument != None

    def _notify_error(self, error_type):

        title = error_type + " Error"
        message = "UNDEFINED ERROR"

        if error_type == "Selection":
            message = "Select two adjacent back tangents to place curve\n \
            (construction line segments)"

        elif error_type == "Invalid_Geometry":
            message = "Selected elements have incorrect geometry"

        QtGui.QMessageBox.critical(None, title, message)

Gui.addCommand('Curve2',Curve2())
