"""
Provides basic geometry utilities for Sketcher.
"""

#pylint: disable=E1601

import re
import FreeCADGui as Gui
import FreeCAD as App
import GeometryObjects
import math

UNIT_X = App.Vector(1.0, 0.0, 0.0)
UNIT_Y = App.Vector(0.0, 1.0, 0.0)
UNIT_Z = App.Vector(0.0, 0.0, 1.0)
ORIGIN = App.Vector(0.0, 0.0, 0.0)

class ElementContainer():
    """
    A data type for storing the active selection by the types of objects selected.
    """

    def __init__(self, geometry, index):
        self.element = geometry
        self.index = index

def _get_pt_of_int(back_tangents):
    """
    Determine the point of intersection between two tangents
    """

    #assume point of intersection is the end point of the
    #first-selected back tangent
    pt_of_int = back_tangents[0].element.EndPoint

    other = back_tangents[0].element.StartPoint

    #test to see if the other point is coincident with
    #the either point on the other back tangent
    #Equality test must accommodate small floating piont error
    if (other - back_tangents[1].element.EndPoint).Length < 0.00001:
        pt_of_int = other

    elif (other - back_tangents[1].element.StartPoint).Length < 0.00001:
        pt_of_int = other

    return pt_of_int

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

def _get_math_lines(vectors, point):
    """
    Given a list of line segment geometry, generate
    and return a corresponding list of math line objects
    whose end points converge on the passed point
    """
    result = []

    for vec in vectors:
        start = point.sub(vec)
        result.append(MathLine.MathLine(start, point))

    return result

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
        point = tangent.element.StartPoint

        #test for equality must accommodate small floating point error
        if (point - pt_of_int).Length < 0.00001:
            point = tangent.element.EndPoint

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
    return ElementContainer(sketch_object.Geometry[index-1], index-1)

def get_intersection (line, point, vector):
    """
    Calculates the point of intersection between the passed line
    segment and the point / direction vector combination

    Arguments:
    line - A Part.LineSegment object
    point - An App.Vector representing a point
    vector - An App.Vector representing a direction

    Returns:
    App.Vector point of intersection
    """

    slope_1 = (line.EndPoint.y - line.StartPoint.y) / \
    (line.EndPoint.x - line.StartPoint.x)

    slope_2 = vector.y / vector.x

    intercept_1 = line.EndPoint.y - (slope_1 * line.EndPoint.x)
    intercept_2 = vector.y - (slope_2 * vector.x)

    intersection = App.Vector(0.0, 0.0, 0.0)

    intersection.x = (intercept_2 - intercept_1) / (slope_1 - slope_2)
    intersection.y = (slope_1 * intersection.x) + intercept_1

    return intersection

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

def getConstraintContent(constriant):

    """
    Deprecated function which retrives
    contraint properties from content attribute.
    Use only for properties not exposed as attributes
    """
    contents = constriant.Content
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

    #iterate the constraints, looking for contraints which are attached
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
