"""
Creates tanget alignment geometry for the Transportation wb
"""
from PySide import QtGui
import FreeCAD as App
import FreeCADGui as Gui
import GeometryUtilities
import Part
import Sketcher

class BackTangent():

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """
        return {'Pixmap'  : 'My_Command_Icon',
                'Accel' : "Shift+B",
                'MenuText': "Back Tangent",
                'ToolTip' : "Add a back tangent",
                'CmdType' : "ForEdit"}

    def Activated(self):
        """
        Executes the tangent construction.
        """
        sketch_obj = App.ActiveDocument.Horizontal_Geometry

        shape_names = []

        if len(Gui.Selection.getSelectionEx()) > 0:
            shape_names = Gui.Selection.getSelectionEx()[0].SubElementNames

        #notify user and abort if more than one object is selected
        if len(shape_names) > 1:
            self._notify_error("Selection")
            return

        #returns a GeometryContainer with the geometry and it's index in the Sketcher Geometry list
        last_tangent = GeometryUtilities.get_last_back_tangent(sketch_obj)

        #if the user selected one object, ensure it is the last back tangent
        #notify user and abort if compare fails
        if len(shape_names) == 1:
            geom = GeometryUtilities.find_geometry(sketch_obj, shape_names[0])

            if not GeometryUtilities.compare(last_tangent, geom):
                self._notify_error("Selection")
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

    def _notify_error(self, error_type):

        title = error_type + " Error"
        message = "UNDEFINED"

        if error_type == "Selection":
            message = "Select the last tangent (or nothing) to append a back \
            tangent"

        elif error_type == "Vertex":
            message = "No unconstrained vertices found on last back tangent"

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

Gui.addCommand('BackTangent', BackTangent())
