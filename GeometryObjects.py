"""
Provides a mathematically-defined geometry objects.
"""

import FreeCAD as App
import Part
import GeometryUtilities as GeoUtils

class Arc2d(object):
    """
    Provides convenience functions for manipulating Part.ArcOfCircle
    objects.
    """

    def __init__(self, arc):
        """
        Initializes the Arc2d object based on the passed arc

        Arguments:
        arc - the arc as a Part.ArcOfCircle
        """

        self.arc = arc
        
        self.parameters = [arc.FirstParameter, arc.LastParameter]

        self.points = self._get_points()

        self.sweep_angle = arc.LastParameter - arc.FirstParameter

    def _get_points(self):
        """
        Returns the start and end point of the curve, ordered
        counterclockwise.
        """

        verts = self.arc.toShape().Vertexes
        start_vec = self.arc.value(self.arc.FirstParameter)
        end_vec = self.arc.value(self.arc.LastParameter)

        for i in range(0, len(verts)):

            v = verts[i].Point

            print "vertex #" + str(i) + ": " + str(v)
            if GeoUtils.compare_vectors(v, start_vec):
                self.start_point = v
                self.start_index = i

            elif GeoUtils.compare_vectors(v, end_vec):
                self.end_point = v
                self.end_index = i

        return [self.start_point, self.end_point]

    def from_vertex_index(self, index):
        """
        Gets the geometrically-ordered curve point index from the 
        passed vertex index.

        Arguments:
        index - the index of the curve's vertex

        Returns:
        Curve index, 0 == self.start_point; 1 == self.end_point
        """

        vtx = self.arc.toShape().Vertexes[index].Point

        result = 0

        if GeoUtils.compare_vectors(vtx, self.end_point):
            result = 1

        return result

class Line2d(object):
    """
    Provides a mathematically-defined line object with basic linear functions,
    f(x), f(y), intersection, and orthogonal transformation.
    Assumes line is defined in X and Y axes.
    """

    def __init__(self, origin, end_point=None, direction=None):
        """
        Generate the key line parameters.  Designed to work with a line
        specified by two end points or by an origin and direction.
        At least one of the optional parameters must be specified.

        Arguments:
        origin (optional) - App.Vector specifying th eorigin point
        end_point (optional) - App.Vector specifying the end point
        direction (optional) - App.Vector specifying the direction

        Notes:
            Z-coordinates are ignored
        """
        self.slope = None
        self.intercept = None
        self.start_point = origin
        self.end_point = end_point

        #Abort if none of the optional parameters are defined
        if direction is None:
            if end_point is None:
                return

        #If direction is undefined, end_point is defined.
        if direction is None:
            direction = self.end_point.sub(self.start_point)

        if direction.Length > 0:
            direction.normalize()

        if direction.x != 0:
            self.slope = direction.y / direction.x

        if self.end_point is None:
            self.end_point = self.start_point.add(direction)

        if self.slope != None:
            self.intercept = self.start_point.y - self.slope * \
            self.start_point.x

    def __str__(self):
        """
        Object string representation
        """

        _vec = "Vector: [" + str(self.start_point) + ", " + \
            str(self.end_point) + "]"

        _slope = "Slope: " + str(self.slope)
        _int = "Intercept: " + str(self.intercept)

        return _vec + "\n" + _slope + "\n" + _int

    @staticmethod
    def from_line_segment(line_segment):
        """
        Generates a new Line2d object from a passed Part.LineSegment
        """

        vtx = line_segment.toShape().Vertexes

        return Line2d(vtx[0].Point, vtx[1].Point)

    def get_side(self, point):
        """
        Returns a value indicating which side of the line the points falls on
        using 1, 0, -1 where 0 = point falls directly on line
        """

        a = self.start_point
        b = self.end_point

        side = (b.x - a.x) * (point.y - a.y) - (b.y - a.y) * (point.x - a.x)

        return GeoUtils.sign(side)
        
    def get_points(self):
        """
        Return the start and end points as a list of App.Vectors
        """

        return [self.start_point, self.end_point]

    def to_line_segment(self):
        """
        Returns the current line as a Part.LineSegment
        """

        return Part.LineSegment(self.start_point, self.end_point)

    def fn_x(self, _x):
        """
        Evaluate the line as a function of x.

        Arguments:
        _x - x coordinate (scalar)

        Returns:
        y coordinate (scalar)
        """

        return self.slope * _x + self.intercept

    def fn_y(self, _y):
        """
        Evaluate the line as a function of y, returning x

        Arguments:
        _y - y coordinate (scalar)

        Returns:
        x coordinate (scalar)
        """

        return (_y - self.intercept) / self.slope

    def is_bounded(self, point):
        """
        Determines if the passed point falls within the line's
        bounding box

        Arguments:
        point - Point to test in App.Vector form

        Returns:
        True / False if within / outside bounding box
        """

        vectors = [App.Vector(self.start_point.x, self.end_point.x), \
            App.Vector(self.start_point.y, self.end_point.y)]

        for i in range(0, 2):

            vec = vectors[i]

            if vec.x > vec.y:
                vec.x, vec.y = vec.y, vec.x

            if not point[i] in range(vec.x, vec.y):
                return False

        return True

    def get_orthogonal(self, point):
        """
        Generates an line object orthogonal to itself from the
        passed point.

        Arguments:
        point - App.Vector of the point from which the orthogonal originates

        Returns:
        MathLine2d object representing the orthogonal
        """

        result = Line2d(point, point)

        #horizontal line case
        if self.slope == 0.0:
            result.slope = None
            result.intercept = None

        #vertical line case
        elif self.slope is None:
            result.slope = 0.0
            result.intercept = point.y

        #everything else
        else:
            result.slope = -1.0 / self.slope
            result.intercept = point.y - result.slope * point.x

        return result

    def intersect(self, line):
        """
        Calculates the point of intersection between the object
        and the passed line object

        Arguments:
        line (As a Line2d object)

        Returns:
        App.Vector specifying the point of intersection
        """

        line_is_vert = (line.slope is None)
        self_is_vert = (self.slope is None)

        if line_is_vert and self_is_vert:
            return None

        #if the passed line is vertical, solve the current line with the
        #vertical line's x-coordinate
        if line_is_vert:
            _x = line.start_point.x
            _y = self.fn_x(_x)

        elif self_is_vert:
            _x = self.start_point.x
            _y = line.fn_x(_x)

        elif self.slope == line.slope:
            return None

        else:
            _x = (line.intercept - self.intercept) / (self.slope - line.slope)
            _y = self.slope * _x + self.intercept

        return App.Vector(_x, _y, 0.0)
