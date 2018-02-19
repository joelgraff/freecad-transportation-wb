"""
Creates tanget alignment geometry for the Transportation wb
"""

from PySide import QtGui
import FreeCAD as App
import FreeCADGui as Gui
import GeometryUtilities as GeoUtils
import Part
import Sketcher
import os

#pylint: disable=E1601

class Tangent():

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/tangent.svg"

        return {'Pixmap'  : icon_path,
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

        #get a list of the geometry attached to the selection via the
        #constraints
        geom = self._get_attached_geometry(selection[0], constraints)

        #With a valid selection and attached geometry,
        #process selection, returning endpoints for the new tangent
        end_points = self._get_endpoints(selection[0], geom)

        #delete existing tangent constraints on the curve geometry
        #and replace with coincident-to-object constraints
        self._replace_curve_constraints(selection[0].index, constraints)

        #create a tangent line with end points which match the curve
        #endpoints or one of the tangent end points
        new_index = self._create_tangent_line(end_points)

        print self.sketch.Geometry[new_index]

        #tangentailly constrain the tangent to curve endpionts and
        #coincidentally constrain to back tangent end points
        self._attach_tangent(new_index, end_points)

        #delete tangent constraints on the curve to the back tangent

        App.ActiveDocument.recompute()
        return

    def _replace_curve_constraints(self, index, constraints):
        """
        Replaces tangent constraints on attached curves with 
        coincident-to-object constraints

        Arguments:

        index - index of the back tangent

        constraints - A list of ElementContainers containing the constraint
        object and it's index

        Returns:

        nothing
        """

        last_index = -1

        for item in constraints:

            constraint = item.element
            target_geo_index = -1
            target_point_index = -1

            if constraint.First == index:
                target_geo_index = constraint.Second
                target_point_index = constraint.SecondPos

            else:
                target_geo_index = constraint.First
                target_point_index = constraint.FirstPos

            cur_index = item.index

            print "deleting: " + str(item.index)
            #test to see if the previous index was higher in the list
            #if so, it's deletion changed the current index
            if (last_index > -1) and (cur_index >= last_index):
                cur_index -= 1
            else:
                last_index = cur_index

            self.sketch.delConstraint(cur_index)

            pt_on_obj = Sketcher.Constraint("PointOnObject",target_geo_index,\
            target_point_index, index)

            self.sketch.addConstraint(pt_on_obj)

            App.ActiveDocument.recompute()

        return

    def _attach_tangent(self, new_index, end_points):
        """
        Attaches the new tangent line to the approrpiate geometry.
        If two curves are present, attaches to the ends of the curves.
        Otherwise, if only one curve is present, attaches to the end
        of the curve and the opposing end of the selection.
        Further, existing tangent constraints on the existing curves
        must be deleted and replaced with coincident-to-object constraints

        Arguments:
        new_index - the index of the newly-created tangent
        end_points - a list of lists.  Each sublist contains the index
        of the shape and the vertex to which the tangent must attach
        """

        tangent = self.sketch.Geometry[new_index].toShape()

        print "new_index: " + str(new_index)
        print "tangent: " + str(tangent)

        print "end points: " + str(end_points)
        indices = []

        #parse the end_point index lists and pair the tangent endpoints
        #with the corresponding attached geometry end points
        for index in end_points:

            print "index: " + str(index)

            shape = self.sketch.Geometry[index[0]].toShape()

            vtx = shape.Vertexes[index[1]]

            print "vertex: " + str(vtx.Point)
            for i in range (0,2):

                print "tangent vtx" + str(i) + ": " + str (tangent.Vertexes[i].Point)

                result = GeoUtils._compare_vectors(vtx.Point, tangent.Vertexes[i].Point)

                if result == 0:
                    
                    point_1 = [index[0], index[1]]
                    point_2 = [new_index, i]
                    point_pair = [point_1, point_2]
                    indices.append(point_pair)

        print "indices: " + str(indices)

        #iterate the pairs, build the constraints, and add them to the sketch
        for pair in indices:

            print str(pair)

            geom = self.sketch.Geometry[pair[0][0]]

            constraint = None

            if (type(geom).__name__=="ArcOfCircle"):
                constraint = Sketcher.Constraint("Tangent", pair[0][0],\
                pair[0][1]+1, pair[1][0], pair[1][1]+1)

            else:
                constraint = Sketcher.Constraint("Coincident", pair[0][0],\
                pair[0][1]+1, pair[1][0], pair[1][1]+1)

            print constraint

            self.sketch.addConstraint(constraint)
            
            App.ActiveDocument.recompute()

        return

    def _create_tangent_line(self, end_points):
        """
        Create a tangent line and append it to the sketch based on
        the passed end points.
        """

        shape_0 = self.sketch.Geometry[end_points[0][0]].toShape()
        shape_1 = self.sketch.Geometry[end_points[1][0]].toShape()

        start_point = shape_0.Vertexes[end_points[0][1]].Point
        end_point = shape_1.Vertexes[end_points[1][1]].Point

        line_segment = Part.LineSegment(start_point, end_point)

        return self.sketch.addGeometry(line_segment)

    def _get_attached_geometry(self, selection, constraints):
        """
        Iterates the constraints and returns a list of the
        geometry which is attached to the selection.

        Arguements:

        selection - the selected back tangent (GeometryContainer)
        constraints - List of Sketcher::Constraints attached to back tangent

        Returns:

        list of geometry / endoint pairs
        """

        attached = []
        index = selection.index

        #Retrieve the attached geometry and the corresponding end points
        for item in constraints:

            constraint = item.element

            #store the indices of the geometry and the
            #constrained point
            geom = [constraint.First, constraint.FirstPos]

            if constraint.First == index:
                geom = [constraint.Second, constraint.SecondPos]

            attached.append(geom)

        return attached

    def _get_endpoints(self, selection, attached):
        """
        Finds the two endpoints along the back tangent for the new tangent.
        Valid cases include two curve endpoints and a single curve endpoint
        with the opposing back tangent vertex as the other endopint.

        Arguments:
        selection - The selected geometry / index as a GeometryContainer
        attached - List of attached constraints

        Returns:
        A list of lists, each sublist containing the index of the shape
        and the end point to which the new tangent will attach.
        """

        end_points = []
        index = selection.index

        #iterate the accumulated targets, acquiring the needed end points
        for geom in attached:

            end_point = [geom[0], geom[1] - 1]
            end_points.append(end_point)

        #If only one tangentially-constrained curve was found,
        #Acquire the back_tangent's opposing vertex as the other end point
        if len(end_points) == 1:

            #get the tangenrt and curve geometry
            tangent = self.sketch.Geometry[index].toShape()
            curve = self.sketch.Geometry[attached[0][0]].toShape()
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
                        end_point = [index, i]
                        end_points.append(end_point)
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
        for i in range(0, len(self.sketch.Constraints)):

            constraint = self.sketch.Constraints[i]

            #look for tangent constraints that are associated with the
            #selected geometry index and store that geometry
            if constraint.Type == "Tangent":

                if constraint.First == index or constraint.Second == index:
                    attached.append(GeoUtils.ElementContainer(constraint, i))

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
        constraints - ElementContainer of constraints and indices
        """

        index = selection.index
        geom = self.sketch.Geometry

        print constraints[0].index

        #validate attached geometry as arcs and return
        for item in constraints:

            constraint = item.element

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

        if (not geo.element.Construction) or \
        (type(geo.element).__name__ != "LineSegment"):

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