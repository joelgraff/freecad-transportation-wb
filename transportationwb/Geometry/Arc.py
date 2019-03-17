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

def discretize_spiral(start_coord, bearing, radius, angle, length, interval, interval_type):
    '''
    Discretizes a spiral curve using the length parameter.  
    '''

    #generate inbound spiral
    #generate circular arc
    #generate outbound spiral

    points = []

    length_mm = length * 304.80
    radius_mm = radius * 304.80

    bearing_in = App.Vector(math.sin(bearing), math.cos(bearing))

    curve_dir = 1.0

    if angle < 0.0:
        curve_dir = -1.0
        angle = abs(angle)

    _Xc = ((length_mm**2) / (6.0 * radius_mm))
    _Yc = (length_mm - ((length_mm**3) / (40 * radius_mm**2)))

    _dY = App.Vector(bearing_in).multiply(_Yc)
    _dX = App.Vector(bearing_in.y, -bearing_in.x, 0.0).multiply(curve_dir).multiply(_Xc)

    theta_spiral = length_mm/(2 * radius_mm)
    arc_start = start_coord.add(_dX.add(_dY))
    arc_coords = [arc_start]
    #arc_coords.extend(_HorizontalAlignment.discretize_arc(arc_start, bearing + (theta_spiral * curve_dir), radius, curve_dir * (angle - (2 * theta_spiral)), interval, interval_type))

    if len(arc_coords) < 2:
        print('Invalid central arc defined for spiral')
        return None

    segment_length = arc_coords[0].distanceToPoint(arc_coords[1])
    segments = int(length_mm / segment_length) + 1

    for _i in range(0, segments):

        _len = float(_i) * segment_length

        _x = (_len ** 3) / (6.0 * radius_mm * length_mm)
        _y = _len - ((_len**5) / (40 * (radius_mm ** 2) * (length_mm**2)))

        _dY = App.Vector(bearing_in).multiply(_y)
        _dX = App.Vector(bearing_in.y, -bearing_in.x, 0.0).multiply(curve_dir).multiply(_x)

        points.append(start_coord.add(_dY.add(_dX)))

    points.extend(arc_coords)

    exit_bearing = bearing + (angle * curve_dir)
    bearing_out = App.Vector(math.sin(exit_bearing), math.cos(exit_bearing), 0.0)

    _dY = App.Vector(bearing_out).multiply(_Yc)
    _dX = App.Vector(-bearing_out.y, bearing_out.x, 0.0).multiply(curve_dir).multiply(_Xc)

    end_coord = points[-1].add(_dY.add(_dX))

    temp = [end_coord]

    for _i in range(1, segments):

        _len = float(_i) * segment_length

        if _len > length_mm:
            _len = length_mm

        _x = (_len ** 3) / (6.0 * radius_mm * length_mm)
        _y = _len - ((_len ** 5) / (40 * (radius_mm ** 2) * (length_mm**2)))

        _dY = App.Vector(-bearing_out).multiply(_y)
        _dX = App.Vector(bearing_out.y, -bearing_out.x, 0.0).multiply(curve_dir).multiply(_x)

        temp.append(end_coord.add(_dY.add(_dX)))

    points.extend(temp[::-1])

    return points

def matrix_test(ST, CT, EN, PI):
    '''
    '''

    result = []

    R_ST = ST.sub(CT)
    R_EN = EN.sub(CT)
    B_ST = PI.sub(ST)
    B_EN = EN.sub(PI)

    points = [R_ST, R_EN, B_ST, B_EN]

    for _i in points:
        result.extend(_i)
        result.append(0.0)

    mat = App.Matrix()
    mat.A = result
    mat_t = App.Matrix(mat)
    mat_t.transpose()

    mat_mult = mat.multiply(mat_t)

    result = []

    mat_mult.A11 = math.sqrt(mat_mult.A11)
    mat_mult.A22 = math.sqrt(mat_mult.A22)
    mat_mult.A33 = math.sqrt(mat_mult.A33)
    mat_mult.A44 = math.sqrt(mat_mult.A44)

    for _i in range(0, 3):

        angles = []

        for _j in range(_i + 1, 4):

            numerator = mat_mult.A[(_i * 4) + _j]

            mag_i = mat_mult.A[(_i * 4) + _i]
            mag_j = mat_mult.A[_j * 4 + _j]

            val = numerator / (mag_i * mag_j)

            angles.append(math.degrees(math.acos(val)))

        result.append(angles[:])

    return mat_mult, result

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

def calc_arc_parameters(arc):

    vectors = None
    bearings = [None, None]

    if all([arc['Start'], arc['PI'], arc['End']]):
        vectors = [arc['PI'].sub(arc['Start']), arc['End'].sub(arc['PI'])]

    elif not (arc['BearingIn']  is None or arc['BearingOut'] is None):
        vectors = [
            Utils.vector_from_angle(arc['BearingIn']),
            Utils.vector_from_angle(arc['BearingOut'])
        ]
        bearings = [arc.get('BearingIn'), arc.get('BearingOut')]

    elif all([arc['Start'], arc['Center'], arc['End']]):
        radii = [arc['Start'].sub(arc['Center']), arc['End'].sub(arc['Center'])]
        vectors = [Utils.vector_ortho(radii)]

    elif arc['Delta'] is None:
        print ('Incomplete arc definition.')
        return None

    #if we've gotten this far and vectors are not defiend, we know:
    # 1. At most, one bearing angle was provided
    # 2. We're missing start / center / end / pi coords
    # 3. We do have a valid delta
    # 
    # Therefore, we can still get what we need if:
    # 1. Start, PI, and Center are defined
    # 2. End, PI and Center are defined
    # 3. Any one of the coords plus
    if not vectors:
        pass

    tangents = [_i.Length for _i in vectors]

    if not Utils.within_tolerance(tangents[0], tangents[1]):
        print ('Inequal tangent lengths')
        return None

    delta = vectors[0].getAngle(vectors[1])
    rot = -1 * math.copysign(1, vectors[0].cross([vectors[1]]).z)

    #calc bearings if the vectors weren't derived from bearing angles
    if (bearings[0] is None or bearings[1] is None):
        bearings = [C.UP.getAngle(_v) for _v in vectors]


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
