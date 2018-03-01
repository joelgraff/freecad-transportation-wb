"""
Generic simple curve generator.  Will generate a curve given no
initial input, a pair of back tangents, a curve and adjacent back tangent,
and a pair of curves.  New curve is generated between selected geometries.
"""
from PySide import QtGui
import FreeCAD as App
import FreeCADGui as Gui
import GeometryUtilities as GeoUtils
import GeometryObjects as GeoObj
import CurveUtilities as CurveUtils
import os
import Part
import Sketcher
import SketchElement as skel

#pylint: disable=E1601

class InsertCurve():

    def GetResources(self):

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/one_center_curve.svg"

        return {'Pixmap'  : icon_path,
                'Accel' : "Shift+0",
                'MenuText': "Simple Curve",
                'ToolTip' : "Add / Insert a simple curve",
                'CmdType' : "For Edit"}

    def IsActive(self):
        """
        Returns class active status
        """
        return Gui.ActiveDocument != None

    def Activated(self):
        """
        Generates an arc based on the selected geometry and returns
        a list containing the arc and it's corresponding back tangents
        """

        if Gui.Selection.getSelection() == []:
            self._notify_error("Selection")
            return

        self.sketch = Gui.Selection.getSelection()[0]

        #validate the selected geometry
        selection = self._validate_selection()

        if selection == None:
            return

        #if one of the geometries is a curve, need to get the opposite
        #back tangent before continuing
        geo_dict = self._get_back_tangents(selection)

        #create a new back tangent and adjust the existing arc
        #so we can place a new arc
        if geo_dict["arc"] != None:

            if geo_dict["end_tangent"] == None:
                return

            #determine the index of the constrained point
            constrained_index = \
                self._get_constrained_index(geo_dict["constraint"])

            #adjust the existing arc
            geo_dict=self._adjust_curve(constrained_index, geo_dict, 0.375)

            #create the arc back tangent
            geo_dict["new_tangent"] = \
                self._generate_new_back_tangent(geo_dict, constrained_index)

            #update the dictionary before adding the arc
            geo_dict["end_tangent"] = geo_dict["new_tangent"]

        #create a new arc based on the specified back tangents
        self._generate_arc(geo_dict)

        return

    def _generate_arc(self, geo_dict):
        """
        Generates a new arc based on passed start and end tangents

        Arguments:
        geo_dict - Geometry dictionary containing selected geometry as
        SketchElements

        Returns:
        geometry dictionary with new arc added as "new_arc"
        """

        return geo_dict

    def _adjust_curve(self, constrained_index, geo_dict, factor):
        """
        Adjusts the length of the arc by the factor value.

        Arguments:
        constrained_index - curve index constrained to the selected tangent
        geo_dict - The dictionary of selected geometry in ElementContainers
        factor - The adjustment factor

        Returns:
        The geometry dictionary with the adjusted arc as an ElementContainer
        object.
        """

        #delete the constraint on the point we're about to move
        self.sketch.delConstraint(geo_dict["constraint"].index)

        App.ActiveDocument.recompute()

        #get references to objects and valueswe're going to use
        arc = geo_dict["arc"]
        curve_2d = GeoObj.Curve2d(arc.element)
        delta_angle = curve_2d.sweep_angle * factor

        idx = curve_2d.from_vertex_index(constrained_index)

        #calculate the parameter for the point's new location
        _u = arc.element.FirstParameter + delta_angle

        if idx == 1:
            _u = arc.element.LastParameter - delta_angle

        point = arc.element.value(_u)

        #move the point, update the dictionary, and return
        self.sketch.movePoint(arc.index, idx + 1, point, 0)

        App.ActiveDocument.recompute()

        geo_dict["arc"].element = self.sketch.Geometry[arc.index]

        return geo_dict

    def _get_constrained_index(self, constraint):
        """
        Given a dictionary of an arc and two tangents, return the
        vertex index of the arc which is constrained by the start tangent

        Arguments:
        constraint - a constraint as an ElementContainer

        Returns:
        index of constrained arc vertex to start tangent
        """
        result = constraint.element.FirstPos

        if result == 0:
            result = constraint.element.SecondPos

        return result - 1

    def _generate_new_back_tangent(self, geo_dict, constrained_index):
        """
        Generates a new back tangent based upon the passed
        arc and adjoining back tangents

        Arguments:
        geo_dict - Geometry dictionary
        constrained_index - Curve point index constrained to the start tangent

        Returns:
        Element Container containing reference and index to new
        back tangent
        """

        arc = geo_dict["arc"]
        start_tangent = geo_dict["start_tangent"]
        end_tangent = geo_dict["end_tangent"]

        curve_2d = GeoObj.Curve2d(arc.element)

        #get the geometrically-ordered curve index
        idx = curve_2d.from_vertex_index(constrained_index)

        print "index: " + str(idx)

        #get the tangent vector and the curve point it passes through
        tan_vec = arc.element.tangent(curve_2d.parameters[idx])[0]
        curve_point = curve_2d.points[idx]

        #create the line which describes the new tangent line
        new_tan_line = GeoObj.Line2d(curve_point, direction = tan_vec)

        #create lines for the existing tangents
        start_tan_line = GeoObj.Line2d.from_line_segment(start_tangent.element)
        end_tan_line = GeoObj.Line2d.from_line_segment(end_tangent.element)

        #set the new tangent line's start end end points to the
        #intersection of the new tangent line and the existing tangents
        new_tan_line.start_point = new_tan_line.intersect(start_tan_line)
        new_tan_line.end_point = new_tan_line.intersect(end_tan_line)

        #create the new geometry, add it to the document, and return the
        #geometry in an ElementContainer
        new_tangent = new_tan_line.to_line_segment()

        new_tan_idx = self.sketch.addGeometry(new_tangent, True)

        App.ActiveDocument.recompute()

        #apply constraints to new tangent, binding it to the other tangents
        sources = [start_tangent, end_tangent]

        for i in range(0,2):
            constraint = Sketcher.Constraint("PointOnObject", \
            new_tan_idx, i+1, sources[i].index)

            self.sketch.addConstraint(constraint)

        App.ActiveDocument.recompute()

        #create constraint to bind curve end point to new tangent
        constraint = Sketcher.Constraint("Tangent", arc.index,\
            idx + 1, new_tan_idx)

        self.sketch.addConstraint(constraint)

        App.ActiveDocument.recompute()

        return skel.SketchElement(new_tangent, new_tan_idx)

    def _get_back_tangents(self, selection):
        """
        Returns the back_tangents valid for the selection

        Arguments:
        selection - An ElementContainer list of the selection geometry

        Returns:
        A dictionary of the geometry:
        "arc" - None if not selected
        "start_tangent" - The first selected back tangent
        "end_tangent" - The second back tangent (selected or discovered)
        "constraint" - The tangent constraint binding the arc to the selected
            back tangent if an arc is selected, None otherwise
        """

        arc = None
        back_tangents = []

        for sel in selection:

            if type(sel.element) == Part.ArcOfCircle:
                arc = sel
            else:
                back_tangents.append(sel)

        result = {"arc": arc, \
                "start_tangent": back_tangents[0], \
                "end_tangent": None, \
                "constraint": None}

        #quit early if two back tangents are already selected
        #or if no arc is selected, but a second back tangent is not found
        if arc == None:

            if (len(back_tangents) == 2):
                result["end_tangent"] = back_tangents[1]
                return result
            else:
                self._notify_error("")
                return None

        opp_tan_idx = 0

        #get ElementContainer list of all constraints attached to the arc
        #constraints = GeoUtils.get_geometry_constraints(self.sketch, arc.index)

        #iterate the constraints to determine our opposing tangent
        #for constraint in constraints:

            #coincident constraints bind two curve endpoints
            #get opposing curve, and find the tangent constraint that
            #binds it to the tangent


        #iterate the constraints looking for the tangent constraints
        #which are applied to the curve
        for i in range (0, self.sketch.ConstraintCount):

            constraint = self.sketch.Constraints[i]

            if constraint.Type == "Tangent":

                tan_idx = 0

                #if the constraint is applied to the curve,
                #determine if the other geometry is the selected
                #back_tangent
                if constraint.First == arc.index:
                    tan_idx = constraint.Second

                elif constraint.Second == arc.index:
                    tan_idx = constraint.First

                #if the tangent index doesn't match the selected
                #tangent, it's the opposite tangent
                #otherwise, save the constraint in the dictionary
                if tan_idx > 0:

                    if tan_idx == back_tangents[0].index:
                        result["constraint"] = skel.SketchElement\
                        (constraint, i)

                    if tan_idx != back_tangents[0].index:
                        opp_tan_idx = tan_idx

        #if we found the opposing back tangent, save it in an ElementContainer
        if opp_tan_idx > 0:

            result["end_tangent"] = skel.SketchElement\
            (self.sketch.Geometry[opp_tan_idx], opp_tan_idx)

        return result

    def _get_arc_vectors(self, arc):
        """
        Returns vectors from center to the end points of the arc
        """

        result = []

        arc_vec = arc.Center.sub(arc.StartPoint)
        result.append(CurveUtils.sort_vectors(arc_vec))

        arc_vec = arc.Center.sub(arc.EndPoint)
        result.append(CurveUtils.sort_vectors(arc_vec))

        return result

    def _validate_selection(self):
        """
        Validates the selected geometry as either construction line segments
        or arcs, ensuring they are constrained to each other properly.

        Arguments:

        None

        Returns:

        ElementContainer List of selection geometry and binding constraint.
        """

        selection = GeoUtils.get_selection(self.sketch)

        if not self._validate_selection_geometry(selection):
            self._notify_error("Invalid Geometry")
            return None

        constraint_list = self._validate_selection_constraints(selection)

        if constraint_list == []:
            self._notify_error("Invalid Constraint")
            return None

        constraint_list = self._validate_selection_bindings(selection,\
        constraint_list)

        if constraint_list == []:
            self._notify_error("Invalid Constraint")
            return None
            
        
        return selection + constraint_list
    
    def _validate_selection_bindings(self, selection, constraints):
        """
        Validates the constraints which bind the selection geometry.

        Arguments:
        selection - A ElementContainer list of the selection geometry
        constraints - A ElementContainer list of the Sketcher.Constraints

        Returns:
        An ElementContainer list of the binding constraints
        """

        result = []

        for constraint in constraints:

            #test for proper connections
            are_connected = False

            for sel in selection:

                are_connected = (constraint.element.First == sel.index) or \
                    (constraint.element.Second == sel.index)

                if not are_connected:
                    break

            #if the constraint binds the selected geometry,
            #append it to the selection list as an ElementContainer
            if are_connected:
                result.append(constraint)
                break                

        return result

    def _validate_selection_constraints(self, selection):
        """
        Determines the types of constraints used to bind the selected
        geometry.

        Arguments:
        selection - Selected geometry passed as ElementContainer list

        Returns:
        ElementContainer List of valid constraint types
        """
        #test for connected geometry
        rng = range(0, self.sketch.ConstraintCount)
        
        two_back_tangents = (type(selection[0].element)==Part.LineSegment) and \
            (type(selection[1].element)==Part.LineSegment)

        result = []

        for i in rng:

            constraint = self.sketch.Constraints[i]

            #Tangent, Coincident, and PointOnObject constraints are valid
            #Curves are tangentially constrained.  Line segments may be
            #coincident or PointOnObject

            is_valid = constraint.Type=="Tangent" and not two_back_tangents

            if not is_valid:

                is_valid = (constraint.Type in ["Coincident", "PointOnObject"])\
                and two_back_tangents

            #skip to next constraint if type check fails
            if not is_valid:
                continue

            result.append (skel.SketchElement(constraint, i))
        
        return result

    def _validate_selection_geometry(self, selection):
        """
        Validates the selected geometry.

        Arguments:

        selection - selected geometry in ElementContainers

        Returns:
        true / false if valid / invalid
        """

        sel_count = len(selection)

        #return empty if nothing is selected
        if sel_count == 0:
            return []

        #only two geometry may be selected
        if sel_count != 2:
            self._notify_error("Selection")
            return None

        #iterate selected geometry ensuring:
        #1- two line segments or one line segment and one arc are selected
        #2 -selected line segments are in construction mode
        valid_geo = True
        last_type = None

        for geo in selection:

            geo_type = type(geo.element)

            if geo_type == Part.LineSegment:
                valid_geo = geo.element.Construction

            elif geo_type == Part.ArcOfCircle:
                valid_geo = (last_type != Part.ArcOfCircle)

            else:
                valid_geo = False

            if not valid_geo:
                break

            last_type = geo_type

        return valid_geo

    def _notify_error(self, error_type):

        title = error_type + " Error"
        message = "UNDEFINED ERROR"

        if error_type == "Selection":
            message = "Select two adjacent back tangents, two adjacent curves, \
            or an adjacent back tangent and curve to place curve."

        elif error_type == "Invalid Geometry":
            message = "Selected elements have incorrect geometry. \
            Select either line segments or arcs.  Line segments must be \
            construction mode."

        elif error_type == "Invalid Constraint":
            message = "Selected geometry are not properly constrained. \
            Geometry must be bound by a tangent constraint."

        QtGui.QMessageBox.critical(None, title, message)

Gui.addCommand('InsertCurve',InsertCurve()) 
