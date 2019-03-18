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
    Calculate the dot products of the vectors among the supplied coordinates
    '''
    result = []

    points = [Utils.safe_sub(ST, CT),
              Utils.safe_sub(EN, CT),
              Utils.safe_sub(PI, ST),
              Utils.safe_sub(EN, PI)
             ]

    for _i in points:
        result.extend(_i)
        result.append(0.0)

    mat = App.Matrix()
    mat.A = result
    mat_t = App.Matrix(mat)
    mat_t.transpose()

    mat_mult = mat.multiply(mat_t)

    mat_list = list(mat_mult.A)

    #square root the length values along the diagonal
    for _i in [0, 5, 10, 15]:
        mat_list[_i] = math.sqrt(mat_mult.A[_i])

    #compute the angles in radians
    mat_list[4] = math.acos(mat_list[4] / (mat_list[0] * mat_list[5]))
    mat_list[9] = math.acos(mat_list[9] / (mat_list[5] * mat_list[10]))
    mat_list[12] = math.acos(mat_list[12] / (mat_list[0] * mat_list[15]))
    mat_list[14] = math.acos(mat_list[14] / (mat_list[10] * mat_list[15]))

    mat_mult.A = mat_list

    return points, mat_mult

def calc_bearings(points):
    '''
    Calculate the bearings from the provided coordinates and angles
    '''

    angles = [-1 * C.UP.getAngle(points[0]),
              -1 * C.UP.getAngle(points[1]),
              -1 * C.UP.getAngle(points[2]),
              -1 * C.UP.getAngle(points[3])
             ]

    rots = [math.copysign(1, C.UP.cross(points[0]).z),
            math.copysign(1, C.UP.cross(points[1]).z),
            math.copysign(1, C.UP.cross(points[2]).z),
            math.copysign(1, C.UP.cross(points[3]).z)
           ]

    #define our bearings by multiplying them by the direction of rotation
    bearings = [_v * rots[_i] for _i, _v in enumerate(angles)]

    print('b1: ', bearings)
    #zero bearings where the result exceeds 2 * pi
    #and adjust for bearings rotating the opposite direction (> pi radians)
    bearings = [_v if abs(_v) < C.TWO_PI else 0.0 for _v in bearings]

    print('b2: ', bearings)
    bearings = [C.TWO_PI + _v if _v < 0.0 else _v for _v in bearings]

    print('b3: ', bearings)
    #adjust the first two (radius) bearings to match the tangent bearings
    bearings[:2] = [_v - C.HALF_PI if _v else 0.0 for _i, _v in enumerate(bearings[:2])]

    return bearings

def calc_delta(mat, arc_delta):
    '''
    Calculate / validate the delta from the matrix
    or user-defined arc parameter
    '''

    #sort deltas so [0] & [1] are the direct central angles
    deltas = [mat.A[_i] for _i in [4, 14, 9, 12]]

    #adjust opposing bearing / radius deltas to solve for central angle
    if deltas[2]:
        deltas[2] -= C.HALF_PI

    if deltas[3]:
        deltas[3] = C.HALF_PI - deltas[3]

    #default unless the calculated deltas work out
    if not any(deltas):
        if not arc_delta:
            return None

    #test to see if adjacent bearing / radius deltas match
    if all(deltas[:2]):
        if not Utils.within_tolerance(deltas[:2]):
            return None

    #test tp see if opposing bearing / radius deltas match
    if all(deltas[2:]):
        if not Utils.within_tolerance(deltas[2:]):
            return None

    #get the first non-zero calcualted delta.
    if not arc_delta:
        arc_delta = [_v for _v in deltas if _v][0]

    return arc_delta

def calc_rotation(vectors):
    '''
    Calculate the rotation of the curve based on the radius / tangent vector pairs
    '''

    rad_rot = -1 * math.copysign(1, vectors[0].cross(vectors[1].z))
    tan_rot = -1 * math.copysign(1, vectors[2].cross(vectors[3].z))

    if tan_rot != rad_rot:
        return 0

    return rad_rot

def calc_lengths(mat, arc_radius, arc_tangent, arc_delta):
    '''
    Calculate / validate the arc radius and tangent from the
    matrix and / or user-defined arc parameters
    '''

    lengths = [mat.A[_i] for _i in [0, 5, 10, 15]]

    if not any(lengths) and not any([arc_tangent, arc_radius]):
        return None

    radii = [_v for _v in lengths[:2] if _v]
    tangents = [_v for _v in lengths[2:] if _v]

    if radii:
        arc_radius = radii[0]

    if tangents:
        arc_tangent = tangents[0]

    if not arc_radius:
        arc_radius = arc_tangent / math.tan(arc_delta / 2.0)

    elif not arc_tangent:
        arc_tangent = arc_radius * math.tan(arc_delta / 2.0)

    return [arc_radius, arc_tangent]

def calc_arc_parameters(arc):

    #compute matrix of coordinate dot-products
    vecs, mat = calc_matrix(
        arc.get('Start'), arc.get('Center'), arc.get('End'), arc.get('PI')
    )

    #calculate the bearings - returns a list of four values
    #first two - start bearing, alst two - end bearing
    bearings = calc_bearings(vecs)

    #validate the delta
    delta = calc_delta(mat, arc.get('Delta'))

    if not delta:
        print('Invalid curve definition: Cannot compute central angle')
        return None

    #calculate the curve direction
    rot = calc_rotation(vecs)

    if not rot:
        print('Unable to determine curve rotation')
        return None

    #validate the [radius, tangent]
    lengths = calc_lengths(mat, arc.get('Radius'), arc.get('Tangent'), delta)

    if not lengths:
        print('Invalid curve definition: Cannot calculate tangent / radius lengths')
        return None

    radius = lengths[0]
    half_delta = delta / 2.0

    #with a valid delta and radius, compute remaining values
    arc = {
        'Direction': rot,
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

    #with all arc parameters, compute missing coordinates

    #return the fully defined arc object

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
