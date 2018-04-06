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
import math
import Part
import Sketcher
import SketchElement as skel

class InsertCurve2():

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

        #need to determine which case we're dealing with:
        #two back tangents selected with no intervening arc
        #or an arc and adjacent back tangent

        self.sketch = Gui.Selection.getSelection()[0]

        selection = GeoUtils.get_selection(self.sketch)

        if selection is None:
            self._notify_error("Selection")
            return

        geo_dict = self._validate_selection(selection)

        print str(geo_dict)
        #case with selected arc and back tangent
        #if geo_dict.has_key("arc"):

            
        return

    def _validate_selection(self, selection):
        """
        Validates the selection against two use cases:
        1,  Two selected back tangents with coincident endpoints
        2.  An arc and back tangent which are attached

        Returns:
        Selected geometry and additional tangents in a dictionary
        """

        if len(selection) != 2:
            return None

       # result = self._validate_two_tangents(selection)

       # if result is None:
        result = self._validate_arc_and_tangent(selection)

        return result

    def _validate_two_tangents(self, selection):
        """
        Validates two selected tangents

        Arguments:
        selection - Selected geometry

        Returns:
        Validated selections
        """

        geo_0 = selection[0]
        geo_1 = selection[1]

        if (not geo_0.type == Part.LineSegment) or \
            (not geo_1.type == Part.LineSegment):
            return 0

        att_0 = geo_0.get_attached_geometry()
        att_1 = geo_1.get_attached_geometry()

        #abort if either is not construction geometry
        if not geo_0.get_element().Construction or \
            not geo_1.get_element().Construction:
            return 1

        #abort if the same geometry is attached to both
        if (set(att_0) & set(att_1)) is None:
            return 2

        #abort if end points are not bound coincidentally
        constraint = geo_0.get_binding_constraint(selection[1].index)

        if constraint.type != "Coincident":
            return 3

        return {"start_tangent": selection[0],
                "end_tangent": selection[1]}

    def _validate_arc_and_tangent(self, selection):
        """
        Validates the selection as an arc and an adjacent back tangent

        Arguments:
        selection - the selected geometry as SketchGeometry

        Returns:
        dictionary of geometry including:
        arc - the selected arc
        start_tangent - the selected tangent
        end_tangent - the opposing tangent
        constraint - the constraint that binds the arc vertex to the
                    selected tangent
        vertex - the index of the vertex bound to the selected tangent
        """

        near_tangent = None
        arc = None

        #abort if not one line and one arc
        for geo in selection:

            if geo.type == Part.LineSegment:
                near_tangent = geo

            elif geo.type == Part.ArcOfCircle:
                arc = geo

        if  (near_tangent is None) or (arc is None):
            return 0

        #abort if the line is not construction
        if not near_tangent.get_element().Construction:
            return 1

        #abort if the arc is construction
        if arc.get_element().Construction:
            return 2

        #abort if arc and line are not attached
        tan_att = near_tangent.get_attached_geometry()

        if not arc.index in tan_att:
            return 3

        #get the opposing tangent
        arc_att = arc.get_attached_geometry()

        far_tangent = set(tan_att) & set(arc_att)

        if far_tangent is None:
            return 4

        far_tangent = self.sketch.Geometry[far_tangent.pop()]

        #get the constraint that binds the arc to the near tangent
        constraint = arc.get_binding_constraint(near_tangent.index)

        #get the index of the arc vertex bound to the near tangent
        vertex_index = constraint.get_element().FirstPos

        if (vertex_index == 0):
            vertex_index = constraint.get_element().SecondPos

        return {"arc": arc,
                "start_tangnet": near_tangent,
                "end_tangent": far_tangent,
                "constraint": constraint,
                "vertex": vertex_index}

    def _notify_error(self, error_type):

        title = error_type + " Error"
        message = "UNDEFINED ERROR"

        if error_type == "Selection":
            message = "Select two adjacent back tangents, two adjacent curves, \
            or an adjacent back tangent and curve to place curve."

        elif error_type == "Attached Geometry":
            message = "Selected elements have attached arc."

        elif error_type == "Invalid Geometry":
            message = "Selected elements have incorrect geometry. \
            Select either line segments or arcs.  Line segments must be \
            construction mode."

        elif error_type == "Invalid Constraint":
            message = "Selected geometry are not properly constrained."

        elif error_type == "Not Coincident":
            message = "Selected geometry do not intersect."

        elif error_type == "No Arc":
            message = "Expected an arc to be selected."

        QtGui.QMessageBox.critical(None, title, message)

Gui.addCommand('InsertCurve',InsertCurve2()) 
