"""
Provides a mathematically-defined line object.
"""

#pylint: disable=E1601

import FreeCAD as App

class MathLine(object):
    """
    Generates the parameters for a valid line equation of the form:
    y = m * x + b

    Additionally, provides testing functions for other geometry against the line.
    """

    def __init__(self, start_point, end_point):
        """
        Generate the key line parameters.
        start_point and end_point must be App.Vector class objects.
        """

        self.start_point = start_point
        self.end_point = end_point

        delta_vector = start_point.sub(end_point)

        self.slope = None
        self.intercept = None

        if delta_vector.x != 0.0:
            self.slope = delta_vector.y / delta_vector.x
            self.intercept = start_point.y - self.slope * start_point.x

    def __str__(self):

        _vec = "Vector: [" + str(self.start_point) + ", " + \
            str(self.end_point) + "]"

        _slope = "Slope: " + str(self.slope)
        _int = "Intercept: " + str(self.intercept)

        return _vec + "\n" + _slope + "\n" + _int

    def fn_x (self, _x):
        """
        Evaluate the line as a function of x, returning y
        """

        return self.slope * _x + self.intercept

    def fn_y (self, _y):
        """
        Evaluate the line as a function of y, returning x
        """

        return (_y - self.intercept) / self.slope

    def get_orthogonal(self, point):
        """
        Generates an line object othogonal to itself from the
        passed point.
        """

        result = MathLine(point, point)

        #horizontal line case
        if self.slope == 0.0:
            result.slope = None
            result.intercept = None            

        #vertical line case
        elif self.slope == None:
            result.slope = 0.0
            result.intercept = point.y

        #everything else
        elif self.slope != 0.0:
            result.slope = -1.0 / self.slope
            result.intercept = point.y - result.slope * point.x

        return result

    def _get_quadrant(self, point):
        """
        Returns the quadrant in which the point resides.
        Quadrant 1: [+x, +y]
        Quadrant 2: [-x, +y]
        Quadrant 3: [-x, -y]
        Quadrant 4: [+x, -y]
        """
        pass
        
    def intersect(self, line):
        """
        Calculates the point of intersection between the object
        and the passed line object
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

        return App.Vector(x, y)

    def is_colinear(self, point):
        """
        Tests to see if the supplied point is colinear with
        the defined line.
        """
        pass        