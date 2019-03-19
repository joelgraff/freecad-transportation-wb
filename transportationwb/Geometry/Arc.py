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

def calc_matrix(vecs):
    '''
    Calculate the 4x4 matrix for the provided points
    '''

    result = []

    for _i in vecs:
        _t = list(_i)

        if len(_t) < 4:
            _t.extend([0.0] * 4 - len(_t))

        result.append(_t)

    mat = App.Matrix()
    mat.A = result

    mat_t = App.Matrix(mat)
    mat_t.transpose()

    mat_mult = mat.multiply(mat_t)

    mat_list = list(mat_mult.A)

    #calculate the vector magnitude on diagonal
    for _i in range[0, 16, 5]:
        mat_list[_i] = math.sqrt(mat_list[_i])

    

def calc_matrix_dep(ST, CT, EN, PI):
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

    #safely calcualte arc cosine
    def acos(_a, _b, _c):
        if not (_b and _c):
            return 0.0
        return math.acos(_a / (_b * _c))

    #compute the angles in radians
    mat_list[4] = acos(mat_list[4], mat_list[0], mat_list[5])
    mat_list[9] = acos(mat_list[9], mat_list[5], mat_list[10])
    mat_list[12] = acos(mat_list[12], mat_list[0], mat_list[15])
    mat_list[13] = acos(mat_list[13], mat_list[5], mat_list[15])
    mat_list[14] = acos(mat_list[14], mat_list[10], mat_list[15])

    mat_mult.A = mat_list

    return points, mat_mult

def calc_bearings(arc, vecs, delta):
    '''
    Calculate the bearings from the provided coordinates and angles
    '''

    #vecs[0, 1] - Radius start / end
    #vecs[2, 3] - Tangent start / end
    angles = [-1 * C.UP.getAngle(vecs['Bearing'][0]),
              -1 * C.UP.getAngle(vecs['Bearing'][1])]

    rots = [math.copysign(1, C.UP.cross(vecs['Bearing'][0]).z),
            math.copysign(1, C.UP.cross(vecs['Bearing'][1]).z)]

    #define our bearings by multiplying them by the direction of rotation
    bearings = [_v * rots[_i] for _i, _v in enumerate(angles)]

    #zero bearings where the result exceeds 2 * pi
    #and adjust for bearings rotating the opposite direction (> pi radians)
    bearings = [_v if abs(_v) < C.TWO_PI else 0.0 for _v in bearings]

    bearings = [C.TWO_PI + _v if _v < 0.0 else _v for _v in bearings]

    print('bearings: ', bearings)

    result = [math.radians(arc['BearingIn']), math.radians(arc['BearingOut'])]

    #abort if we have absolutely no bearing data to work with
    if not bearings and not result:
        return None

    #abort if calculated difference exceeds tolerance (bad curve definition)
    if all(bearings) and not Utils.within_tolerance(bearings):
        print('Incorrect curve definition: bearing mismatch')
        return None

    for _i, _bearing in enumerate(bearings):

        _b = result[_i]

        #if the calculated bearing is outside tolerance with the user, default to calculated
        if not Utils.within_tolerance(_bearing, result[_i]):
            result[_i] = _bearing

    return result

def calc_delta(arc, vecs):
    '''
    Calculate / validate the delta from the matrix
    or user-defined arc parameter
    '''
    delta = arc.get('Delta')
    angle = 0.0
    rot = arc.get('Direction')
    
    if rot:
        if rot == 'cw':
            rot = 1
        else:
            rot = -1

    if all(vecs['Radius']):
        _vecs = vecs['Radius']

    elif all(vecs['Bearing']):
        _vecs = vecs['Bearing']

    elif vecs['Middle']:
        _vecs = [vecs['Middle']]
        _vecs.append([_v for _v in vecs['Radius'] if _v][0])

    return Utils.get_rotation(vecs), vecs[0].getAngle(vecs[1])

def calc_lengths(arc, vecs, delta):
    '''
    Calculate / validate the arc radius and tangent from the
    matrix and / or user-defined arc parameters
    '''

    arc_radius = arc['Radius']
    arc_tangent = arc['Tangent']

    radius = arc_radius
    tangent = arc_tangent

    #get the calculated lengths from coordinate vectors, if possible
    if any(vecs['Radius']):
        radius = [_v.Length for _v in vecs['Radius'] if _v][0]

    if any(vecs['Tangent']):
        tangent = [_v.Length for _v in vecs['Tangent'] if _v][0]

    #abort if neither are defined
    if not (radius and tangent):
        return None

    #if either is None, define according to the other.
    if not radius:
        radius = tangent / math.tan(delta / 2.0)

    if not tangent:
        tangent = radius * math.tan(delta / 2.0)

    #default to the user-defined values if within tolerance of the calculated
    if Utils.within_tolerance(radius, arc_radius):
        radius = arc_radius

    if Utils.within_tolerance(tangent, arc_tangent):
        tangent = arc_tangent

    return [radius, tangent]

def fix_vectors(vecs, delta, rot):
    '''
    Given the passed data, fill in any missing vectors
    '''
    rad_vec = vecs['Radius']
    tan_vec = vecs['Tangent']
    mid_vec = vecs['Middle']

    _sin = rot * math.sin(delta / 2.0)
    _cos = rot * math.cos(delta / 2.0)

    _init_delta = 0.0

    if mid_vec:
        init_delta = C.UP.getAngle(mid_vec)
    elif rad_vec[0]:
        init_delta = C.UP.getAngle(rad_vec[0]) + (delta / 2.0)
    elif rad_vec[1]:
        init_delta = C.UP.getAngle(rad_vec[1]) - (delta / 2.0)
    elif tan_vec[0]:
        init_delta = C.UP.getAngle(tan_vec[0]) - (math.pi - delta) / 2.0
    elif tan_vec[1]:
        init_delta = C.Up.getAngle(tan_vec[1]) - (math.pi + delta) / 2.0

    angle = init_delta + delta

    if not rad_vec[0]:
        rad_vec[0] = App.Vector(math.sin(angle / 2.0),
                                math.cos(angle / 2.0)).multiply(-1.0 * rot)

    if not rad_vec[1]:
        rad_vec[1] = App.Vector(math.sin(angle / 2.0),
                                math.cos(angle / 2.0)).multiply(rot)

    if not tan_vec[0]:
        tan_vec[0] = App.Vector(math.sin((math.pi - angle) / 2.0),
                                math.cos((math.pi - angle) / 2.0)).multiply(-1.0 * rot)

    if not tan_vec[1]:
        tan_vec[1] = App.Vector(math.sin((math.pi - angle) / 2.0),
                                math.cos((math.pi - angle) / 2.0)).multiply(-1.0 * rot)

    if not vecs['Middle']:
        middle_vec = App.Vector(math.sin(init_delta), math.cos(init_delta)).multiply(rot)

    return {'Radius': rad_vec, 'Tangent': tan_vec, 'Middle': middle_vec}

def calc_arc_parameters(arc):

    vecs = {'Radius': [Utils.safe_sub(arc.get('Start'), arc.get('Center'), True),
                       Utils.safe_sub(arc.get('End'), arc.get('Center'), True)],
            'Bearing': [Utils.safe_sub(arc.get('PI'), arc.get('Start'), True),
                        Utils.safe_sub(arc.get('End'), arc.get('PI'), True)],
            'Middle': Utils.safe_sub(arc.get('PI'), arc.get('Center'), True)
           }

    #validate the delta
    rot, delta = calc_delta(arc, vecs)

    if not (delta and rot):
        print('Invalid curve definition: Cannot compute central angle')
        return None

    lengths = calc_lengths(arc, vecs, delta)

    if not lengths:
        print('Invalid curve definition: Cannot compute tangent or radius lengths')
        return None

    vecs = fix_vectors(vecs, delta, rot)

    #calculate the bearings - returns a list of four values
    #first two - start bearing, last two - end bearing
    bearings = calc_bearings(arc, vecs, delta)

    if not bearings:
        print ('Invalid curve definition')
        return None

    radius = lengths[0]
    half_delta = delta / 2.0
    #scale_factor = 1.0 / Units.scale_factor()

    #with a valid delta and radius, compute remaining values
    return {
        'Direction': rot,
        'Delta': math.degrees(delta),
        'Radius': radius,
        'Length': radius * delta,
        'Tangent': radius * math.tan(half_delta),
        'Chord': 2 * radius * math.sin(half_delta),
        'External': radius * ((1 / math.cos(half_delta) - 1)),
        'MiddleOrd': radius * (1 - math.cos(half_delta)),
        'BearingIn': math.degrees(bearings[0]),
        'BearingOut': math.degrees(bearings[1]),
        'Start': arc['Start'],
        'Center': arc['Center'],
        'End': arc['End'],
        'PI': arc['PI']
    }

def arc_parameter_test(excludes=None):
    '''
    '''
    scale_factor = 1.0 / Units.scale_factor()

    radius = 670.00
    delta = 50.3161
    half_delta = math.radians(delta) / 2.0

    arc = {
        'Direction': -1,
        'Delta': delta,
        'Radius': radius,
        'Length': radius * math.radians(delta),
        'Tangent': radius * math.tan(half_delta),
        'Chord': 2 * radius * math.sin(half_delta),
        'External': radius * ((1 / math.cos(half_delta) - 1)),
        'MiddleOrd': radius * (1 - math.cos(half_delta)),
        'BearingIn': 139.3986,
        'BearingOut': 89.0825,
        'Start': App.Vector(122056.0603640062, -142398.20717496306, 0.0).multiply(scale_factor),
        'Center': App.Vector (277108.1622932797, -9495.910944558627, 0.0).multiply(scale_factor),
        'End': App.Vector (280378.2141876281, -213685.7280672748, 0.0).multiply(scale_factor),
        'PI': App.Vector (184476.32163324804, -215221.57431973785, 0.0).multiply(scale_factor)
    }

    if excludes:
        for _exclude in excludes:
            arc[_exclude] = None

    return calc_arc_parameters(arc)

#############
#test output:
#############
#{'Direction': -1.0, 'Delta': 50.3161, 'Radius': 670.0, 'Length': 588.3816798810216, 'Tangent': 314.67910063712156, 'Chord': 569.6563702820052, 'External': 70.21816809491217, 'MiddleOrd': 63.55717091445238, 'BearingIn': 139.3986, 'BearingOut': 89.0825, 'Start': Vector (400.44639227036157, -467.1857190779628, 0.0), 'Center': Vector (909.1475140855633, -31.154563466399697, 0.0), 'End': Vector (919.8760307993049, -701.0686616380407, 0.0), 'PI': Vector (605.2372756996326, -706.1075272957279, 0.0)}

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
