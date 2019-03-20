# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

'''
Useful math functions and constants
'''

__title__ = "Math.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import math

import FreeCAD as App

from transportationwb.ScriptedObjectSupport.Const import Const

    #Regular expressions for detecting stations
    #rex_station = re.compile(r'[0-9]+\+[0-9]{2}\.[0-9]{2,}')
    #rex_near_station = re.compile(r'(?:[0-9]+\+?)?[0-9]{1,2}(?:\.[0-9]*)?')
class Constants(Const):
    '''
    Useful math constants
    '''

    TWO_PI      = math.pi * 2.0             #   2 * pi in radians
    HALF_PI     = math.pi / 2.0             #   1/2 * pi in radians
    ONE_RADIAN  = 180 / math.pi             #   one radian in degrees
    TOLERANCE   = 0.0001                    #   tolerance for differences in measurements
    UP          = App.Vector(0.0, 1.0, 0.0) #   Up vector

def safe_sub(lhs, rhs, return_None=False):
    '''
    Safely subtract two vectors.
    Returns an empty vector or None if either vector is None
    '''

    if not lhs or not rhs:

        if return_None:
            return None

        return App.Vector()

    return lhs.sub(rhs)

def safe_radians(value):
    '''
    Convert a floating point value from degrees to radians,
    handle None / invalid type conditions
    '''

    if value is None:
        return 0.0

    if not isinstance(value, float):
        return 0.0

    return math.radians(value)

def to_float(value):
    '''
    Return true if string value is float
    '''

    result = None

    if isinstance(value, list):

        result = []

        for _v in value:

            _f = to_float(_v)

            if _f is None:
                return None

            result.append(_f)

        return result

    try:
        result = float(value)

    except:
        pass

    return result

def to_int(value):
    '''
    Return true if string is an integer
    '''

    result = None

    if isinstance(value, list):

        result = []

        for _v in value:

            _f = to_int(_v)

            if not _f:
                return None

            result.append(_f)

        return result

    try:
        result = int(float(value))

    except:
        pass

    return result

def get_rotation(in_vector, out_vector = None):
    '''
    Returns the rotation as a signed integer:
    1 = cw, -1 = ccw, 0 = fail

    if in_vector is an instance, out_vector is ignored.
    '''
    _in = in_vector
    _out = out_vector

    if isinstance(_in, list):
        if not all(_in):
            return 0

        _out = in_vector[1]
        _in = in_vector[0]

    return -1.0 * math.copysign(1, _in.cross(_out).z)

def get_bearing(vector):
    '''
    Returns the absolute bearing of the passed vector.
    Bearing is measured clockwise from +y 'north' (0,1,0)
    Vector is a list of coordinates or an App.Vector
    '''

    result = vector

    if isinstance(vector, list):
        result = App.Vector(vector)

    if not isinstance(vector, App.Vector):
        return None

    rot = get_rotation(Constants.UP, result)

    angle = rot * Constants.UP.getAngle(result)

    print ('bearing_rot = ', rot)
    print('bearing_angle = ', angle)
    if angle < 0.0:
        angle += Constants.TWO_PI

    return angle

def within_tolerance(lhs, rhs=None):
    '''
    Determine if two values are within a pre-defined tolerance

    lhs / rhs - values to compare.  rhs may be none if lhs is an array

    Array comparisons check every value against every other, and error if any checks fail
    '''

    tol_check = True

    if isinstance(lhs, list):

        for _i in range(0, len(lhs) - 1):

            rhs = lhs[_i:]

            for _val in rhs:

                if not abs(lhs[_i] - _val) < Constants.TOLERANCE:
                    return False

    elif rhs is None:
        return False

    else:
        return abs(lhs-rhs) < Constants.TOLERANCE

    return tol_check

def vector_ortho(vector):
    '''
    Returns the orthogonal of a 2D vector as (-y, x)
    '''
    
    vec_list = vector

    if not isinstance(vector, list):
        vec_list = [vector]

    result = []

    for vec in vec_list:
        result.append(App.Vector(-vec.y, vec.x, 0.0))

    if len(result) == 1:
        return result[0]

    return result

def vector_from_angle(angle):
    '''
    Returns a vector form a given angle in radians
    '''

    return App.Vector(math.sin(angle), math.cos(angle), 0.0)

def distance_bearing_to_coordinates(distance, bearing):
    '''
    Converts a distance and bearing (in degrees) to cartesian coordinates
    '''

    #convert the bearing to radians, ensuring it falls witin [0.0, 2 * pi)]
    _b = math.radians(bearing) % Constants.two_pi

    return App.Vector(math.sin(_b), math.cos(_b), 0.0).multiply(distance)

def coordinates_to_distance_bearing(prev_coord, next_coord):
    '''
    Given two coordinates in (x,y,z) format, calculate the distance between them
    and the bearing from prev to next
    '''

    distance = (next_coord-prev_coord).Length
    deltas = next_coord - prev_coord

    #calculate the directed bearing of the x and yh deltas
    bearing = math.atan2(deltas[0], deltas[1])

    if bearing < 0.0:
        bearing += math.pi * 2.0

    return (distance, math.degrees(bearing))

def doc_to_radius(value, is_metric=False, station_length=0):
    '''
    Converts degree of curve value to radius
    Assumes a default 100 feet for english units and 1000 meters for metric.
    Custom station lengths can be defined using the station_length parameter
    '''

    if station_length == 0:

        station_length = 100.0

        if is_metric:
            station_length = 1000.0

    return Constants.one_radian * (station_length / value)

def station_to_distance(station, equations):
    '''
    Given a station and equations along an alignment,
    convert the station to the distance from the start of the alignment
    '''

    _s = station

    try:
        _s = float(station)

    except:
        print('Station not floating point value')
        return 0

    start_sta = -1
    end_sta = -1
    distance = 0.0

    for eqn in equations:

        #the equation back is the end of the current range
        end_sta = eqn[0]

        #less than zero - initial station equation
        if not (start_sta < 0.0 or end_sta < 0.0):

            #if the station falls between two values,
            #calculate the final segment length and break out
            if _s <= end_sta and _s >= start_sta:
                distance += _s - start_sta
                break

            #accumulate distance across this station range
            distance += end_sta - start_sta

        #forward is the starting station for the next range
        start = eqn[1]

    return distance

def scrub_stationing(station):
    '''
    Accepts a text string representing a station and
    scrubs it, returning a valid floating point value, -1 if invalid
    '''

    scrub = station.replace('+', '')

    try:
        float(scrub)

    except:
        return -1

    return float(scrub)
