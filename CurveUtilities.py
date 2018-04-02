"""
Provides basic utilities for curve construction in Sketcher
"""

from PySide import QtGui
import math
import GeometryUtilities as GeoUtils
import FreeCAD as App
import Part
import GeometryObjects as GeoObj

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

def sort_vectors(vectors):
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

def create_arc(params):
    """
    Generate arc based on passed parameters specifying:
     - Centerpoint (arc location)
     - Radius
     - Start angle (radians)
     - Sweep angle (radians)

     Arguments:
     params - dictionary containing the necessary parameters

     Returns:
     The new geometry to add to the sketch
    """

    circle_part = Part.Circle(params["location"], UNIT_Z, params["radius"])

    #return a list with the resulting arc and the vectors in proper order
    result = Part.ArcOfCircle(circle_part, params["start_angle"],\
        params["sweep_angle"])

    return result

def _create_arc(back_tangents):
    """
    Generate arc parameters based on the passed tangents.
    Parameters create an arc which fits the internal angle of the
    tangents.
    """

    #get the point of intersection
    pt_of_int = back_tangents[0].get_element().intersect2d( \
        back_tangents[1].get_element(), Part.Plane())[0]

    pt_of_int = App.Vector(pt_of_int[0],pt_of_int[1],0)

    #get directed vectors from the point of intersection
    vectors = GeoUtils._get_vectors(back_tangents, pt_of_int)

    #sort the vectors such that the first one is the starting vector for
    #the arc's counter-clockwise rotation
    result = sort_vectors(vectors)

    vectors = result

    #get the length of the shorter back_tangnet, and
    #reduce to 3/8th's original size
    length = GeoUtils._get_shorter(vectors).Length * 0.375

    #normalize and scale the vectors for the default back tangent length
    for i in range(0,2):
        vectors[i].normalize()
        vectors[i].multiply(length)

    #calculate the radius points back from the point of intersection
    #along the directed vectors
    #and create lines representing the back tangents
    radius_points = []
    ortho_lines = []

    for vec in vectors:
        rad_pt = pt_of_int.sub(vec)
        radius_points.append(rad_pt)

        line = GeoObj.Line2d(pt_of_int, direction = vec)
        ortho_lines.append(line.get_orthogonal(rad_pt))

    #calculate the point of intersection between the two orhogonal lines
    #and save the result as the arc's center point
    center_point = ortho_lines[0].intersect(ortho_lines[1])

    ortho_vectors = [radius_points[0].sub(center_point), \
        radius_points[1].sub(center_point)]

    offset = 0.0
    start_ortho = ortho_vectors[0]

    print "vector length: " + str(length)
    print "bt0: " + str(back_tangents[0].get_element())
    print "bt1: " + str(back_tangents[1].get_element())
    print str(result)
    print str(vectors)
    print "point of intersection: " + str(pt_of_int)
    print "radius points: " + str(radius_points)
    print "center point: " + str(center_point)
    print "ortho_vectors: " + str(ortho_vectors)

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

    #return a list with the resulting arc and the vectors in proper order
    result = [Part.ArcOfCircle(circle_part, start_angle, sweep_angle), vectors]

    return result

def validate_selection(sketch):

    #get the selected objects as GeometryContainer objects
    selection = GeoUtils.get_selection(sketch)

    #need to have exactly two selections
    if len(selection) != 2:

        _notify_error("Selection")
        return None

    #selections must be construction mode and line segments
    for geo in selection:

        if (not geo.get_element().Construction) or \
            (geo.type != Part.LineSegment):

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