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

    def _validate_selection(self):

        #get the selected objects as GeometryContainer objects
        selection = GeoUtils.get_selection(self.sketch)

        #need to have exactly two selections
        if len(selection) != 2:

            self._notify_error("Selection")
            return None

        #selections must be construction mode and line segments
        for geo in selection:

            if (not geo.element.Construction) or \
            (type(geo.element).__name__ != "LineSegment"):

                self._notify_error("Invalid Geometry")
                return None

        #selections must be adjacent
        for constraint in self.sketch.Constraints:

            content = GeoUtils.getConstraintContent(constraint)

            if content["Type"] != "1":
                continue

            if constraint.First != selection[0].index:
                if constraint.Second != selection[0].index:
                    continue

            if constraint.First != selection[1].index:
                if constraint.Second != selection[1].index:
                    continue

            #if we made it this far, the constraint is coincident and
            #binds both selection elements.  We're done.
            return selection

        self._notify_error("")
        
        return None

    def _notify_error(self, error_type):

        title = error_type + " Error"
        message = "UNDEFINED ERROR"

        if error_type == "Selection":
            message = "Select two adjacent back tangents to place curve\n \
            (construction line segments)"

        elif error_type == "Invalid_Geometry":
            message = "Selected elements have incorrect geometry"

        QtGui.QMessageBox.critical(None, title, message)

Gui.addCommand('Curve1',Curve1()) 
