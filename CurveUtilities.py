"""
Provides basic utilities for curve construction in Sketcher
"""

#pylint: disable=E1601

from PySide import QtGui
import math
import GeometryUtilities as GeoUtils
import FreeCAD as App
import Part
import MathLine

UNIT_X = App.Vector(1.0, 0.0, 0.0)
UNIT_Y = App.Vector(0.0, 1.0, 0.0)
UNIT_Z = App.Vector(0.0, 0.0, 1.0)
ORIGIN = App.Vector(0.0, 0.0, 0.0)

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

def create_arc(back_tangents):
    """
    Generate arc parameters based on the passed tangents.
    Parameters create an arc which fits the internal angle of the
    tangents.
    """

    #get the point of intersection
    pt_of_int = _get_pt_of_int(back_tangents)

    #get directed vectors from the point of intersection
    vectors = GeoUtils._get_vectors(back_tangents, pt_of_int)

    #sort the vectors such that the first one is the starting vector for
    #the arc's counter-clockwise rotation
    result = _sort_vectors(vectors)

    #note if the vectors have been swapped
    swapped_tangents = GeoUtils._compare_vectors (result[0], vectors[0])

    vectors = result

    #get the length of the shorter back_tangnet, and
    #reduce to 3/8th's original size
    length = GeoUtils._get_shorter(vectors).Length * 0.375

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
    math_lines = GeoUtils._get_math_lines(vectors, pt_of_int)

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

def validate_selection(sketch):

    #get the selected objects as GeometryContainer objects
    selection = GeoUtils.get_selection(sketch)

    #need to have exactly two selections
    if len(selection) != 2:

        _notify_error("Selection")
        return None

    print selection

    #selections must be construction mode and line segments
    for geo in selection:

        print geo

        if (not geo.element.Construction) or \
        (type(geo.element).__name__ != "LineSegment"):

            _notify_error("Invalid Geometry")
            return None

    #selections must be adjacent
    for constraint in sketch.Constraints:

        if constraint.Type == 1:
            continue

        if constraint.First != selection[0].index:
            if constraint.Second != selection[0].index:
                continue

        if constraint.First != selection[1].index:
            if constraint.Second != selection[1].index:
                continue

        #if we made it this far, the constraint is coincident and
        #binds both selection elements.  We're done.
        return selection

    _notify_error("")
        
    return None

def _notify_error(error_type):

    title = error_type + " Error"
    message = "UNDEFINED ERROR"

    if error_type == "Selection":
        message = "Select two adjacent back tangents to place curve\n \
        (construction line segments)"

    elif error_type == "Invalid_Geometry":
        message = "Selected elements have incorrect geometry"

    QtGui.QMessageBox.critical(None, title, message)