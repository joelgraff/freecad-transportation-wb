import FreeCADGui as Gui
import FreeCAD as App
import GeometryUtilities as GeoUtils
import CurveUtilities as CurveUtils
import Sketcher
import MathLine
import os

#pylint: disable=E1601

class Curve1():
    """
    Curve1 generates a 1-center curve.  User is required to select two adjacent
    backtangents for correct curve placement.
    """

    def GetResources(self):

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/one_center_curve.svg"

        return {'Pixmap'  : icon_path,
                'Accel' : "Shift+1",
                'MenuText': "One-Center Curve",
                'ToolTip' : "Add a one-center curve",
                'CmdType' : "For Edit"}

    def Activated(self):

        if Gui.Selection.getSelection() == []:
            return

        self.sketch = Gui.Selection.getSelection()[0]

        #abort if two adjacent back tangents are not selected
        back_tangents = CurveUtils.validate_selection(self.sketch)

        if back_tangents is None:
            return

        #build he arc, oriented w.r.t. the selected back tangents
        result = CurveUtils.create_arc(back_tangents)

        arc = result[0]

        #swap back tangents if they were swapped in the arc computation
        if result[1] != 0:
   
            x = back_tangents[0]
            back_tangents[0] = back_tangents[1]
            back_tangents[1] = x

        #Create a new curve
        curve_index = self.sketch.addGeometry(arc, False)

        App.ActiveDocument.recompute()

        #constrain curve to selected back tangents
        self._constrain_curve(curve_index, back_tangents)

        return

    def IsActive(self):
        """
        Returns class active status
        """
        return Gui.ActiveDocument != None

    def _constrain_curve(self, curve_index, back_tangents):
        """
        Constrains a curve to the supplied back tangents
        """

        constraints = []

        constraints.append(Sketcher.Constraint("Tangent", curve_index, \
            1, back_tangents[0].index))

        App.ActiveDocument.recompute()

        constraints.append(Sketcher.Constraint("Tangent", curve_index, \
            2, back_tangents[1].index))

        App.ActiveDocument.recompute()

        for constraint in constraints:
            self.sketch.addConstraint(constraint)
            App.ActiveDocument.recompute()

Gui.addCommand('Curve1',Curve1()) 
