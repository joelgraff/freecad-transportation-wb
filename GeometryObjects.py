"""
Provides a mathematically-defined geometry objects.
"""

#pylint: disable=E1601

import FreeCAD as App
import Part

class Line2d(object):
    """
    Provides a mathematically-defined line object with basic linear functions,
    f(x), f(y), intersection, and orthogonal transformation.
    Assumes line is defined in X and Y axes.
    """

    def __init__(self, origin, end_point = None, direction = None):
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
        if direction == None:
            if end_point == None:
                return

        #If direction is undefined, end_point is defined.
        if direction == None:
            direction = self.end_point.sub(self.start_point)

        direction.normalize()

        if self.end_point == None:
            self.end_point = self.start_point.add(direction)

        self.slope = direction.y / direction.x
        self.intercept = self.start_point.y - self.slope * self.start_point.x

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
        Generates a new MathLine object from a passed Part.LineSegment
        """

        vtx = line_segment.toShape().Vertexes

        return Line2d(vtx[0], vtx[1])

    def to_line_segment(self):
        """
        Returns the current line as a Part.LineSegment
        """

        result = Part.LineSegment(self.start_point, self.end_point)

    def fn_x (self, _x):
        """
        Evaluate the line as a function of x.
        
        Arguments:
        _x - x coordinate (scalar)

        Returns:
        y coordinate (scalar)
        """

        return self.slope * _x + self.intercept

    def fn_y (self, _y):
        """
        Evaluate the line as a function of y, returning x

        Arguments:
        _y - y coordinate (scalar)

        Returns:
        x coordinate (scalar)
        """

        return (_y - self.intercept) / self.slope

    def get_orthogonal(self, point):
        """
        Generates an line object othogonal to itself from the
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
        elif self.slope == None:
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

        line_is_vert = (line.slope == None)
        self_is_vert = (self.slope == None)

        if line_is_vert and self_is_vert:
            return None

        #if the passed line is vertical, solve the current line with the
        #vertical line's x-coordinate
        if line_is_vert:
            x = line.start_point.x
            y = self.fn_x(x)

        elif self_is_vert:
            x = self.start_point.x
            y = line.fn_x(x)

        else:
            x = (line.intercept - self.intercept) / (self.slope - line.slope)
            y = self.slope * x + self.intercept

        return App.Vector(x, y, 0.0)