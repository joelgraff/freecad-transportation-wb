"""
Creates tanget alignment geometry for the Transportation wb
"""
from PySide import QtGui
import FreeCAD as App
import FreeCADGui as Gui
import GeometryUtilities as GeoUtils
import Part
import Sketcher

#pylint: disable=E1601

class Tangent():

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """
        return {'Pixmap'  : 'My_Command_Icon',
                'Accel' : "Shift+T",
                'MenuText': "Tangent",
                'ToolTip' : "Add a tangent",
                'CmdType' : "ForEdit"}

    def Activated(self):
        """
        Executes the tangent construction.
        """

        if Gui.Selection.getSelection() == []:
            self._notify_error("Selection")

        self.sketch = Gui.Selection.getSelection()[0]

        #validate, ensuring no inappropriate constraints
        selection = self._validate_selection()
        
        #result from an invalid selction
        if selection == None:
            return

        #validate the attached constrains as tangents, that only one or two
        #are attached, and that their adjoinging geometry are Part.ArcOfCircle
        constraints = self._get_attached_constraints(selection[0])

        if constraints == None:
            return

        if self._validate_attached_constraints(selection[0], \
            constraints) == None:
            return

        #With a valid selection and attached constraints and geometry,
        #process selection, returning endpoints for the new tangent
        end_points = self._get_endpoints(selection[0], constraints)

        print end_points

        #create a tangent line with end points which match the curve
        #endpoints or one of the tangent end points
        new_index = self._create_tangent_line(end_points)

        #tangentailly constrain the tangent to curve endpionts and
        #coincidentally constrain to back tangent end points

        #delete tangent constraints on the curve to the back tangent

        App.ActiveDocument.recompute()
        return

    def _create_tangent_line(self, end_points):
        """
        Create a tangent line and append it to the sketch based on
        the passed end points.
        """

        line_segment = Part.LineSegment(end_points[0], end_points[1])

        return self.sketch.addGeometry(line_segment)

    def _get_endpoints(self, selection, constraints):
        """
        Finds the two endpoints along the back tangent for the new tangent.
        Valid cases include two curve endpoints and a single curve endpoint
        with the opposing back tangent vertex as the other endopint.

        Arguments:
        index - The index of the selected geometry
        selection - The selected geometry / index as a GeometryContainer
        constraints - List of attached constraints
        """

        targets = []
        index = selection.index

        #Retrieve the attached geometry and the corresponding end points
        for constraint in constraints:

            #store the indices of the geometry and the
            #constrained point
            target = [constraint.First, constraint.FirstPos]

            if constraint.First == index:
                target = [constraint.Second, constraint.SecondPos]

            targets.append(target)

        end_points = []

        #iterate the accumulated targets, acquiring the needed end points
        for target in targets:
            shape = self.sketch.Geometry[target[0]].toShape()
            end_points.append(shape.Vertexes[target[1] - 1].Point)

        #If only one tangentially-constrained curve was found,
        #Acquire the back_tangent's opposing vertex as the other end point
        if len(end_points) == 1:

            #get the tangenrt and curve geometry
            tangent = self.sketch.Geometry[index].toShape()
            curve = self.sketch.Geometry[targets[0][0]].toShape()
            curve_center = curve.Curve.Center

            #create vectors to the ends of the tangent and ends of the curve
            #from the curve's center point
            curve_vec = [curve.Vertexes[0].Point.sub(curve_center), \
                curve.Vertexes[1].Point.sub(curve_center)]

            tangent_vec = [tangent.Vertexes[0].Point.sub(curve_center), \
                tangent.Vertexes[1].Point.sub(curve_center)]

            #compute cross-productes between the tangent and curve vectors
            #the tangent vector whose cross product does not change between
            #the curve vectors points to the tangent vertex we want
            for i in range(0,2):

                is_reversed = True
                direction = 0

                for c_vec in curve_vec:

                    result = self._get_sign(tangent_vec[i].cross(c_vec).z)

                    if direction == 0:
                        direction = result
                        continue
                    else:
                        is_reversed = (direction != result)
                
                    if not is_reversed:
                        end_points.append(tangent.Vertexes[i].Point)
                        break
                
                if len(end_points) == 2:
                    break

        return end_points

    def _get_sign(self, value):
        """
        Return the sign of a value.
        -1 = Less than zero
        +1 = Greater than zero
        0 = Zero
        """

        if value > 0:
            return 1

        if value < 0:
            return -1

        return 0

    def _get_attached_constraints(self, selection):
        """
        Finds the tangent constraints applied to the passed geometry
        and returns them.  Returns None if constraints are not tangent or
        too many or too few are attached.

        Arguments:
        selection - The selected geometry / index as a GeometryContainer
        """

        index = selection.index
        attached = []

        #iterate the constraints, looking for attached geometry
        for constraint in self.sketch.Constraints:

            #look for tangent constraints that are associated with the
            #selected geometry index and store that geometry
            if constraint.Type == "Tangent":

                if constraint.First == index or constraint.Second == index:
                    attached.append(constraint)        

        #abort if no geometry is attached or if more than two tangent
        #constraints are applied
        if len(attached) == 0 or len(attached) > 2:
            self._notify_error("Invalid_Constraints")
            return None

        return attached

    def _validate_attached_constraints(self, selection, constraints):
        """
        Takes a list of constraint indices and validates their attached
        geometry as curves (Part.ArcOfCircle).

        Arguments:
        selection - The selected geometry / index in a GeometryContainer
        constraints - list of constraints attached to selection
        """

        index = selection.index
        geom = self.sketch.Geometry

        #validate attached geometry as arcs and return
        for constraint in constraints:

            target_idx = -1

            if constraint.First == index:
                target_idx = constraint.Second

            elif constraint.Second == index:
                target_idx = constraint.First

            if type(geom[target_idx]).__name__ != "ArcOfCircle":
                self._notify_error("Invalid_Attached_Geometry")
                return None

        return constraints

    def _validate_selection(self):
        """
        Processes the current selected geometry, ensuring it is a
        construction-mode line segment
        """
        #get the selected objects as GeometryContainer objects
        selection = GeoUtils.get_selection(self.sketch)

        #must have only one selection
        if len(selection) != 1:

            self._notify_error("Selection")
            return None

        #selection must be a construction mode line segment
        geo = selection[0]

        if (not geo.geometry.Construction) or \
        (type(geo.geometry).__name__ != "LineSegment"):

            self._notify_error("Invalid_Geometry")
            return None

        return selection

    def _notify_error(self, error_type):
        """
        Notifies user with a dialog box of an error.

        Arguments:
        error_type - String indicating the type of error.
                     Unhandled strings default to undefined error.
        """
        title = error_type + " Error"
        message = "UNDEFINED ERROR"

        if error_type == "Selection":
            message = "Select a single back tangent."

        elif error_type == "Invalid_Geometry":
            message = "Selected elements have incorrect geometry"

        elif error_type == "Invalid_Constraints":
            message = "Selected elements have invalid constraints"

        elif error_type == "Invalid_Attached_Geometry":
            message = "Attached elements are not curves."
            
        QtGui.QMessageBox.critical(None, title, message)

        return

    def IsActive(self):
        """
        Returns true if there is an active document
        """
        return True

Gui.addCommand('Tangent', Tangent())