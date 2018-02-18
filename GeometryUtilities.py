"""
Provides basic selection services for the Transportation Workbench.
These services include selection validation for specific operations (append/
insert), as well as testing for specific conditions (connected/constrained geometry)
"""

#pylint: disable=E1601

import re
import math
import FreeCADGui as Gui
import FreeCAD as App
import Part
import MathLine

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
        start = point - vec
        result.append(MathLine.MathLine(start, point))

    return result

def _get_shorter(vectors):
    """
    Compare the lengths of the vectors, returning the shorter one.
    """

    if vectors[0].Length < vectors[1].Length:
        return vectors[0]

    return vectors[1]
    
def _sort_vectors(vectors):
    """
    Takes a list of two App.Vectors and orders them
    such that the first is rotated counterclockwise from the second.
    """

    vec0 = vectors[0]
    vec1 = vectors[1]

    cross_product = vec0.cross(vectors[1])

    result = [vec0, vec1]

    if cross_product.z > 0.0:

        result = [vec1, vec0]

    return result
    
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

def _compare_vectors(lhs, rhs):
    """
    Compares the length of two vectors.  If the length
    is less than 0.00001 (1 * 10^-5), they are equivalent.
    Retruns:
    0 - equivalent
    -1 - lhs < rhs
    1 - lhs > rhs
    """

    delta = lhs.Length - rhs.Length

    if delta < 0.0:
        return -1

    if delta > 0.00001:
        return 1

    return 0

def create_arc(back_tangents):
    """
    Generate arc parameters based on the passed tangents.
    Parameters create an arc which fits the internal angle of the
    tangents.
    """

    #get the point of intersection
    pt_of_int = _get_pt_of_int(back_tangents)

    #get directed vectors from the point of intersection
    vectors = _get_vectors(back_tangents, pt_of_int)

    #sort the vectors such that the first one is the starting vector for
    #the arc's counter-clockwise rotation
    result = _sort_vectors(vectors)

    #note if the vectors have been swapped
    swapped_tangents = _compare_vectors (result[0], vectors[0])

    vectors = result

    #get the length of the shorter back_tangnet, and
    #reduce to 3/8th's original size
    length = _get_shorter(vectors).Length * 0.375

    #normalize and scale the vectors for the default back tangent length
    for i in range(0,2):
        print str(vectors[i])
        vectors[i].normalize()
        vectors[i].multiply(length)

    #calculate the radius points back from the point of intersection
    #along the directed vectors
    radius_points = []

    for vec in vectors:
        radius_points.append(pt_of_int.sub(vec))

    #generate two MathLine objects based on the actual geometry
    #but with the starting points set at the point of intersection
    math_lines = _get_math_lines(vectors, pt_of_int)

    ortho_lines = []
    ortho_vectors = []

    #get the orthogonal lines using the radius points
    for i in range(0, 2):
        ortho_lines.append(math_lines[i].get_orthogonal(radius_points[i]))

    #calculate the point of intersection between the two orhogonal lines
    #and save the result as the arc's center point
    center_point = ortho_lines[0].intersect(ortho_lines[1])

    ortho_vectors = [radius_points[0].sub(center_point), \
        radius_points[1].sub(center_point)]

    offset = 0.0
    start_ortho = ortho_vectors[0]

    if radius_points[0].y > pt_of_int.y:
        offset = math.pi

    start_angle = math.pi / 2.0

    if start_ortho.x == 0.0:
        if start_ortho.y < 0.0:
            start_angle *= -1.0

    if ortho_vectors[0].x != 0.0:
        start_angle = offset+math.atan(ortho_vectors[0].y / ortho_vectors[0].x)

    sweep_angle = ortho_vectors[1].getAngle(ortho_vectors[0]) + start_angle

    circle_part = Part.Circle(center_point, UNIT_Z, ortho_vectors[0].Length)

    result = []

    #return a list with the resulting arc and a boolean indicating whether
    #or not the tangent order was swapped
    result.append (Part.ArcOfCircle(circle_part, start_angle, sweep_angle))
    result.append (swapped_tangents)

    return result

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
