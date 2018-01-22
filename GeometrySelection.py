"""
Provides basic selection services for the Transportation Workbench.
These services include selection validation for specific operations (append/
insert), as well as testing for specific conditions (connected/constrained geometry)
"""

from PySide import QtGui
import FreeCADGui as Gui
import Part

class SelectionContainer():
    """
    A data type for storing the active selection by the types of objects selected.
    """

    def __init__(self):
        self.vertices = []
        self.lines = []
        self.curves = []

def is_insert_selection():
    """
    Returns true if two adjacent objects are selected.
    """

    selection = Gui.Selection.getSelectionEx()

    if len(selection) != 2:
        return False

    object_one = selection[0].SubObjects[0]
    object_two = selection[1].SubObjects[0]

    return is_connected(object_one, object_two)

def is_connected(object_one, object_two):
    """
    Returns true for objects which share at least one common Vertex.
    """

    for vtx_one in object_one.Vertexes:
        for vtx_two in object_two.Vertexes:
            if (vtx_one.X == vtx_two.X) and (vtx_one.y == vtx_two.y):
                return True

    return False

def is_append_selection():
    """
    Returns true if the last object (or no object) is selected.
    """

    return False

def notify_selection_error(title):
    """
    Notifies user in case of selection error.
    Title of error is passed as an argument.
    """

    QtGui.QMessageBox.critical(
        None, title, "Select two adjacent elements to insert between.")


def get_selection():
    """
    Returns a SelectionContainer object which categorizes
    the selected objects by type: Line, Curve, and Vertex.
    """

    selected = Gui.Selection.getSelectionEx()[0].SubObjects
    sel_len = len(selected)
    result = SelectionContainer()

    for _x in range(0, sel_len):

        shape_type = selected[_x].ShapeType

        if shape_type == 'Vertex':
            result.vertices.append(selected[_x])

        elif shape_type == 'Edge':

            if 'Line' in str(selected[_x].Curve):
                result.lines.append(selected[_x])
            else:
                result.curves.append(selected[_x])
