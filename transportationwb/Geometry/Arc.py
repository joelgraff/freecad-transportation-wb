# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX Joel Graff <monograff76@gmail.com>                 *
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
Arc generation tools
'''

import math
import FreeCAD as App
import Draft

from transportationwb.ScriptedObjectSupport import Units, Utils
from transportationwb.ScriptedObjectSupport.Utils import Constants as C

def calc_matrix(ST, CT, EN, PI):
    '''
    '''
    result = []

    R_ST = Utils.safe_sub(ST, CT)
    R_EN = Utils.safe_sub(EN, CT)
    B_ST = Utils.safe_sub(PI, ST)
    B_EN = Utils.safe_sub(EN, PI)

    points = [R_ST, R_EN, B_ST, B_EN]

    for _i in points:
        result.extend(_i)
        result.append(0.0)

    mat = App.Matrix()
    mat.A = result
    mat_t = App.Matrix(mat)
    mat_t.transpose()

    mat_mult = mat.multiply(mat_t)

    #square root the length values along the diagonal
    for _i in [0, 5, 10, 15]:
        mat_mult.a[_i] = math.sqrt(mat_list[_i])

    return mat_mult

def calc_arc_parameters(arc):

    mat = calc_matrix(arc.get['Start'], arc.get['Center'], arc.get['End'], arc.get['PI'])

    #indices of the length and delta values
    delta_indices = [4, 9, 12, 14]

    #sort deltas so [0] & [1] are the direct values
    deltas = [mat.A[_i] for _i in [4, 14, 9, 12]]

    delta = 0.0

    if not any(deltas):
        if not arc['delta']:
            print('Invalid curve definition: Cannot compute central angle')
            return None

        else:
            delta = arc['delta']
            

    if all(deltas[:2]):
        if not Utils.within_tolerance(deltas[:2]):
            print('Invalid curve definition: Invalid radius and/or tangents')
            return None

    if all(deltas[2:]):
        if not Utils.within_tolerance():
            print('Invalid curve definition: Invalid radius and/or tangents')


    if deltas[1]:
        deltas[1] -= C.half_pi

    if deltas[2]:
        deltas[2] = 90 - deltas[2]

    length_indices = [0, 5, 10, 15]

    lengths = [mat.A[_i] for _i in [0, 5, 10, 15]]

    if all(lengths[2:]):
        if not Utils.within_tolerance(lengths[0:2]):
            print('Invalid curve definition: Unequal tangent lengths')
            return None

    #build list of angles
    for _i in range(0, 3):

        angles = []

        for _j in range(_i + 1, 4):

            numerator = mat_mult.A[(_i * 4) + _j]
            mag_i = mat_mult.A[_i * 5]
            mag_j = mat_mult.A[_j * 5]

            val = numerator / (mag_i * mag_j)

            angles.append(math.degrees(math.acos(val)))

        result.append(angles[:])

def arc_parameter_test(excludes = None):
    '''
    '''

    scale_factor = 1.0 / Units.scale_factor()

    radius = 670.00
    delta = math.radians(50.3161)
    half_delta = delta / 2.0

    arc = {
        'Direction': -1,
        'Delta': delta,
        'Radius': radius,
        'Length': radius * delta,
        'Tangent': radius * math.tan(half_delta),
        'Chord': 2 * radius * math.sin(half_delta),
        'External': radius * ((1 / math.cos(half_delta) - 1)),
        'MiddleOrd': radius * (1 - math.cos(half_delta)),
        'BearingIn': math.radians(139.3986),
        'BearingOut': math.radians(89.0825),
        'Start': App.Vector(122056.0603640062, -142398.20717496306, 0.0).multiply(scale_factor),
        'Center': App.Vector (277108.1622932797, -9495.910944558627, 0.0).multiply(scale_factor),
        'End': App.Vector (280378.2141876281, -213685.7280672748, 0.0).multiply(scale_factor),
        'PI': App.Vector (184476.32163324804, -215221.57431973785, 0.0).multiply(scale_factor)
    }

    return calc_arc_parameters(arc)



def calc_arc_parameters_dep(arc):
    '''
    points:
    0 - PC
    1 - CTR
    2 - PT
    3 - PI
    '''

    '''
    TEST PARAMETERS:

    a = [App.Vector (-86.952232, 94.215736, 0.0), App.Vector (0.0, 0.0, 0.0), App.Vector (96.326775, 84.60762, 0.0), App.Vector (9.611027, 183.334518, 0.0)]
    a1 = [App.Vector (-87.275208, -93.916885, 0.0), App.Vector (0.0, 0.0, 0.0), App.Vector (96.63192, -84.259216, 0.0), App.Vector (9.628621, -183.354034, 0.0)]

    }
    '''
    #must have at least three points
    #if len([True for _i in points if _i]) < 3:
    #    return None

    #piecemeal assembly to test for missing PI or Center point
    vectors = [App.Vector()] * 4

    #substitute in bearing vectors, if possible
    #vectors = ...

    bearing_only = arc['Center'] is None
    radius_only = arc['PI'] is None

    if not radius_only:
        vectors[2:] = [arc['PI'].sub(arc['Start']), arc['End'].sub(arc['PI'])]

    if not bearing_only:
        vectors[0:2] = [arc['Center'].sub(arc['Start']), arc['Center'].sub(arc['End'])]

    lengths = [_i.Length for _i in vectors]

    print(lengths)
    #substitute in radius if not calcualted
    #if not (lengths[0] amd lengths[1]):
    #if next (lengths[2] and lengths[3])

    if (lengths[0] - lengths [1]) > 0.0001 or (lengths[2] - lengths[3]) > 0.0001:
        print('inequal radii / tangents')
        return None

    #vector pairs for angle computations
    pairs = [(0, 1), (2, 3)]

    delta = [vectors[_i[0]].getAngle(vectors[_i[1]]) for _i in pairs]
    delta = [_i for _i in delta if abs(_i) < math.pi][0]

    #if delta == 0.0:
        #return if no delta is provided with arc,
        #otherwise assign

    #first, second, fifth and sixth for -cw, +ccw
    rot = [vectors[_i[0]].cross(vectors[_i[1]]) for _i in pairs]
    rot = -1 * math.copysign(1, [_i for _i in rot if _i != App.Vector()][0].z)

    #if rot == 0:
        #return if rotation is not provided

    _up = App.Vector(0.0, 1.0, 0.0)

    bearings = [_up.getAngle(vectors[_i]) for _i in range(0, 4)]
    bearings = [_i for _i in bearings if abs(_i) < math.pi]

    ###### Calc all arc values and return a dictionary

    ###radius_only: calc tangent, bearing
    ###bearing_only: calc delta, radius

    half_delta = delta / 2.0

    radius = lengths[0]
    tangent = lengths[1]
    bearing_in = bearings[0]
    bearing_out = bearings[1]
    radius_in = bearings[0]
    radius_out = bearings[1]
    _ctr = arc['Center']
    _pi = arc['PI']

    if bearing_only:
        print('bearing only')
        radius /= math.tan(half_delta)
        #radius_in -= rot * 180.0
        #radius_out += rot * 180.0
        _ctr = arc['Start'].sub(App.Vector(-vectors[2].y, vectors[2].x, 0.0).normalize().multiply(radius * rot))

    if radius_only:
        print('radius only')
        tangent *= math.tan(half_delta)
        #bearing_in += rot * 180.0
        #bearing_out -= rot * 180.0
        _pi = arc['Start'].add(App.Vector(-vectors[0].y, vectors[0].x, 0.0).normalize().multiply
        (tangent * rot))

    result = {
        'Direction': rot,
        'Delta': delta,
        'Radius': radius,
        'Length': radius * delta,
        'Tangent': tangent,
        'Chord': 2 * radius * math.sin(half_delta),
        'External': radius * ((1 / math.cos(half_delta) - 1)),
        'MiddleOrd': radius * (1 - math.cos(half_delta)),
        'BearingIn': bearing_in,
        'BearingOut': bearing_out,
        'Start': arc['Start'],
        'Center': _ctr,
        'End': arc['End'],
        'PI': _pi
    }

    return [result, vectors, lengths, delta, rot, bearings]

def calc_arc_delta(bearing_in, bearing_out):
    '''
    Returns the curve direction and central angle (dir, delta)
    bearing_in / out = bearings in radians

    dir = -1 for ccw, 1 for cw
    delta = central angle in radians
    '''

    _ca = bearing_out - bearing_in

    return _ca / abs(_ca), abs(_ca)

def calc_arc_parameters_dep(points):
    '''
    Returns a list of the key parameters of an arc based on it's start,
    end, and center coordinates.
    points[0] - Start
    points[1] - End
    points[2] - Center
    '''
    up_vec = App.Vector(0.0, 1.0, 0.0)

    start_point = points[0]
    end_point = points[1]
    center_point = points[2]

    start_rad = center_point.sub(start_point).normalize()
    end_rad = center_point.sub(end_point).normalize()

    radius = start_rad.Length

    #arbitrary check to ensure start / end radius vectors are the same length
    if radius - end_rad.Length > 0.0001:
        print('Points do not form a circular arc')
        return None

    angle = start_rad.getAngle(end_rad)
    direction = start_rad.cross(end_rad).z
    start_dir = App.Vector(start_rad.y, -start_rad.x, 0.0)
    end_dir = App.Vector(end_rad.y, -end_rad.x, 0.0)

    #calcualte the bearings
    bearing_in = up_vec.getAngle(start_dir)
    bearing_out = up_vec.getAngle(end_dir)

    if up_vec.cross(start_dir).z > 0.0:
        bearing_in += math.pi

    if up_vec.cross(end_dir).z > 0.0:
        bearing_out += math.pi

    clock_dir = 'cw'

    if direction > 0.0:
        clock_dir = 'ccw'

    return {
        'Radius': radius, 'Delta': angle, 'Direction': clock_dir, 'InBearing': bearing_in,
        'BearingOut': bearing_out
    }

def valiate(arc):
    '''
    Validate the arc parameters

    arc must containg either 3 coordinates (PI, Start, End, Center)
    or two angles (bearings, delta), a length (radius, tangent) and 1 coord (start, end, center, pi)
    '''

    
    #arcs need start / center / end points, or PI, bearing_in
def get_points(arc_dict, interval, interval_type='Segment', start_coord = App.Vector()):
    '''
    Discretize an arc into the specified segments.
    Resulting list of coordinates omits provided starting point and
    concludes with end point

    arc_dict    - A dictionary containing key elemnts:
        Direction   - non-zero.  <0 = ccw, >0 = cw
        Radius      - in document units (non-zero, positive)
        Delta       - in radians (non-zero, positive)
        BearingIn   - true north starting bearing in radians (0 to 2*pi)
        BearingOut  - true north ending bearing in radians (0 to 2*pi)

    interval    - value for the interval type (non-zero, positive)

    interval_type: (defaults to segment for invalid values)
        'Segment'   - subdivide into n equal segments
        'Interval'  - subdivide into fixed length segments
        'Tolerance' - limit error between segment and curve

    Points are returned references to start_coord
    '''

    angle = arc_dict['Delta']
    direction = arc_dict['Direction']
    bearing_in = math.radians(arc_dict['InBearing'])
    radius = arc_dict['Radius']

    #validate paramters
    if not direction or not angle:
        direction, angle = calc_arc_delta(bearing_in, math.radians(arc_dict['OutBearing']))

    if any([_x <= 0 for _x in [radius, angle, interval]]):
        return None

    if not 0.0 < bearing_in < (math.pi * 2.0):
        return None

    scale_factor = Units.scale_factor()

    _forward = App.Vector(math.sin(bearing_in), math.cos(bearing_in), 0.0)
    _right = App.Vector(_forward.y, -_forward.x, 0.0)

    radius_mm = radius * scale_factor
    result = [App.Vector()]

    #define the incremental angle for segment calculations, defaulting to 'Segment'
    _delta = angle / interval

    if interval_type == 'Interval':
        _delta = interval / radius

    elif interval_type == 'Tolerance':
        _delta = 2.0 * math.acos(1 - (interval / radius))

    #pre-calculate the segment deltas, increasing from zero to the central angle
    segment_deltas = [float(_i + 1) * _delta for _i in range(0, int(angle / _delta) + 1)]
    segment_deltas[-1] = angle

    for delta in segment_deltas:

        _dfw = App.Vector(_forward).multiply(math.sin(delta))
        _drt = App.Vector(_right).multiply(direction * (1 - math.cos(delta)))

        result.append(start_coord.add(_dfw.add(_drt).multiply(radius_mm)))

    return result
