"""
Provides basic geometry utilities for Sketcher.
"""

#pylint: disable=E1601

import re
import FreeCADGui as Gui
import FreeCAD as App
import GeometryObjects
import math
import SketchElement as skel

UNIT_X = App.Vector(1.0, 0.0, 0.0)
UNIT_Y = App.Vector(0.0, 1.0, 0.0)
UNIT_Z = App.Vector(0.0, 0.0, 1.0)
ORIGIN = App.Vector(0.0, 0.0, 0.0)

def _get_arc_angles(vectors):
    """
    Return the start and sweep angles for an arc
    given two vectors.
    """
    cross_product = vectors[0].cross(vectors[1])

    start_vector = vectors[0]

    if (cross_product < 0):
        start_vector = vectors[1]

    start_angle = (math.pi / 2.0)-start_vector.getAngle(UNIT_X)
    sweep_angle = math.pi - vectors[1].getAngle(vectors[0])

    angles = [start_angle, sweep_angle]

    return angles

def _get_shorter(vectors):
    """
    Compare the lengths of the vectors, returning the shorter one.
    """

    if vectors[0].Length < vectors[1].Length:
        return vectors[0]

    return vectors[1]
    
def _get_vectors(back_tangents, pt_of_int):
    """
    Convert geometry container objects to App.Vectors
    directed away from the passed pint of intersection.
    """

    result = []

    #iterate each tangent, converting it into a directed vector
    #toward the point of intersection
    for tangent in back_tangents:
        point = tangent.get_element().StartPoint

        #test for equality must accommodate small floating point error
        if (point - pt_of_int).Length < 0.00001:
            point = tangent.get_element().EndPoint

        vec = App.Vector(pt_of_int.sub(point))
        result.append(vec)

    return result

def compare_vectors(lhs, rhs):
    """
    Compares the length of two vectors.  If the difference between
    individual points is less than 0.00001 (1 * 10^-5), they are equivalent.

    Returns:
    True / False if identical / different
    """

    for i in range (0,3):
        if abs(lhs[i] - rhs[i]) > 0.00001:
            return False

    return True

def find_geometry(sketch_object, shape_name):
    """
    Looks up the geometry based on the provided shape name
    """

    #skip if a vertex is passed
    if shape_name[:6] == "Vertex":
        return None

    index = int(filter(str.isdigit, shape_name))

    #return a GeometryContainer object with a reference to the geometry
    #and it's index in the Geometry list
    return skel.SketchGeometry(sketch_object, index-1)

def sign(value):

    if value > 0:
        return 1
    elif value < 0:
        return -1

    return 0

def get_selection(sketch_object):
    """
    Return a list of geometry which corresponds to the selected shapes
    """
    result = []

    if len(Gui.Selection.getSelectionEx()) == 0:
        return result

    shape_names = Gui.Selection.getSelectionEx()[0].SubElementNames

    for shape_name in shape_names:
        result.append(find_geometry(sketch_object, shape_name))

    return result

def compare(geom_1, geom_2):
    """
    Matches two geometry objects by comparing class type,
    and vertex coordinates.  Cannot distinguish between
    identical objects overlaid on one another
    """

    #return false for any failing test, otherwise, return true

    if type(geom_1) != type(geom_2):
        return False

    if geom_1.StartPoint != geom_2.StartPoint:
        return False

    if geom_1.EndPoint != geom_2.EndPoint:
        return False

    return True

def getConstraintContent(constraint):

    """
    Deprecated function which retrives
    contraint properties from content attribute.
    Use only for properties not exposed as attributes
    """
    contents = constraint.Content
    values = contents.split(" ")
    result = {}

    for value in values:
        pair = re.split('[=\"]+', value)

        if len(pair) > 1:
            result[pair[0]] = pair[1]

    return result

def get_unconstrained_vertices(sketch_object, geometry_container):
    """
    For the given geometry, return which vertices are unconstrained.
    Array is returned.  True elements are unconstrained.
    """

    vertices = [True, True]
    falses = [False, False]

    #iterate the constraints, looking for constraints which are attached
    #to the passed geometry.  Set the corresponding vertex index to False
    for constraint in sketch_object.Constraints:

        #parse the content string into a list
        #firstPos = 9, secondPos = 11
        constraint_content = re.split(r'[\s="]+', constraint.Content)

        if constraint.First == geometry_container.index:
            vertices[int(constraint_content[9])-1] = False

        elif constraint.Second == geometry_container.index:
            vertices[int(constraint_content[13])-1] = False

        if vertices == falses:
            break

    return vertices
