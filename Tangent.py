"""
Creates tanget alignment geometry for the Transportation wb
"""
from PySide import QtGui
import FreeCAD as App
import FreeCADGui as Gui
import GeometryUtilities
import Part
import Sketcher

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

        tangent = self._validate_selection()

        if tangent == None:
            return

        #attach a new construction line to the end of the last one found
        vertex_constrained = GeometryUtilities.\
            get_unconstrained_vertices(sketch_obj, last_tangent)

        vtx_index = -1

        for i in range(0, len(vertex_constrained) - 1):
            if not vertex_constrained[i]:
                vtx_index = i

        if vtx_index == -1:
            self._notify_error("Vertex")

        vtx = last_tangent.geometry.Vertexes[vtx_index]

        start_point = App.Vector(vtx.X, vtx.Y)
        end_point = App.Vector(vtx.X + 100.0, vtx.Y + 100.0)
        new_index = sketch_obj.AddGeometry(Part.LineSegment(start_point, end_point))

        sketch_obj.addConstraint(Sketcher.\
        Constraint('Coincident', geom.index, vtx_index, new_index, 1))

def _validate_selection(self):

        #get the selected objects as GeometryContainer objects
        selection = GeoUtils.get_selection(self.sketch)

        #need to have exactly two selections
        if len(selection) != 1:

            self._notify_error("Selection")
            return None

        #selection must be a construction mode line segment
        geo = selection[0]

        if (not geo.geometry.Construction) or \
        (type(geo.geometry).__name__ != "LineSegment"):

            self._notify_error("Invalid Geometry")
            return None

        has_tangent_constraint = False

        #selections must be adjacent
        for constraint in self.sketch.Constraints:

            content = GeoUtils.getConstraintContent(constraint)

            has_tangent_constraint = content["Type"] == "5"

            if (has_tangent_constraint):
                return geo

        self._notify_error("Invalid_Geometry")

        return None

    def _notify_error(self, error_type):

        title = error_type + " Error"
        message = "UNDEFINED ERROR"

        if error_type == "Selection":
            message = "Select a single back tangent."

        elif error_type == "Invalid_Geometry":
            message = "Selected elements have incorrect geometry"
            
        QtGui.QMessageBox.critical(None, title, message)

        
        #validate the selection, returning if invalid
        #selected_geometry = self._getSelection()

        #int count = len(selected_geometry)

        #create the new geometry
        #newGeometry = Part.LineSegment (
         #   FreeCAD.Vector (0.0, 0.0), FreeCAD.Vector (1.0, 1.0))

        #insert the geometry
        #unless it's true north, then add a angle constraint

        return

    def IsActive(self):
        """
        Returns true if there is an active document
        """
        return True

Gui.addCommand('Tangent', Tangent())
