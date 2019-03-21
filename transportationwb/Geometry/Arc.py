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
import numpy

from transportationwb.ScriptedObjectSupport import Units
from transportationwb.Geometry import Support
from transportationwb.ScriptedObjectSupport.Utils import Const, Constants as C

def _create_geo_func():

    _fn = []

    #create a square matrix of empty lambdas
    for _i in range(0, 6):
        _fn.append([lambda _x: 0.0]*7)

    #the seventh row is for the bearing with the UP vector,
    #so we only need the direct angle
    _fn.append([lambda _x: _x]*7)

    _fn[1][0] = lambda _x: _x
    _fn[3][2] = _fn[1][0]

    _fn[5][0] = lambda _x: (2 * _x) - math.pi
    _fn[4][3] = _fn[5][0]

    _fn[5][1] = lambda _x: math.pi - (2 * _x)
    _fn[4][2] = _fn[5][1]

    _fn[3][0] = lambda _x: _x - C.HALF_PI
    _fn[2][1] = lambda _x: C.HALF_PI - _x

    _fn[4][0] = lambda _x: 2 * _x
    _fn[4][1] = _fn[4][0]
    _fn[5][2] = _fn[4][0]
    _fn[5][3] = _fn[4][0]

    _fn[6][0] = lambda _x, _delta: _x + C.HALF_PI
    _fn[6][1] = lambda _x, _delta: _x - _delta + C.HALF_PI
    _fn[6][2] = lambda _x, _delta: _x
    _fn[6][3] = lambda _x, _delta: _x - _delta
    _fn[6][4] = lambda _x, _delta: _x + (C.HALF_PI + (_delta / 2.0))
    _fn[6][5] = lambda _x, _delta: _x - (_delta / 2.0)

    return _fn

class _GEO(Const):

    FUNC = _create_geo_func()

def calc_scalar_matrix(vecs):
    '''
    Calculate the square matrix of scalars
    for the provided vectors
    '''
    #ensure list is a list of lists (not vectors)
    #and create the matrix
    mat_list = [list(_v) for _v in vecs]
    mat_list.append(list(C.UP))

    mat = numpy.matrix(mat_list)
    result = mat * mat.T

    #abort for non-square matrices
    if result.shape[0] != result.shape[1] != 6:
        return None

    #calculate the magnitudes first (minus the UP vector)
    for _i in range(0, 6):
        result.A[_i][_i] = math.sqrt(result.A[_i][_i])

    #calculate the delta for the lower left side
    for _i in range(0, 7):
        _d1 = result.A[_i][_i]

        for _j in range(0, _i):
            _d2 = result.A[_j][_j]
            _n = result.A[_i][_j]
            _angle = math.acos(_n / (_d1 * _d2))

            #compute the arc central angle for all but the last row
            if _i < 6:
                result.A[_i][_j] = _GEO.FUNC[_i][_j](_angle)
            else:
                result.A[_i][_j] = _angle

    #lower left half contains angles, diagonal contains scalars
    return result

def calc_bearings(arc, mat, delta, rot):
    '''
    Calculate the bearings from the matrix and delta value
    '''

    bearing_in = arc.get['BearingIn']

    for _i in range(0, 6):
        mat.A[6][_i] = _GEO.FUNC[6][_i](mat.A[6][_i], delta)

    _b = [_v for _v in mat.A[6] if _v]

    if _b:
        if not Support.within_tolerance(_b[0], bearing_in)
            bearing_in = _b[0]

    if not bearing_in:
        return None

    return {'BearingIn': bearing_in, 'BearingOut', bearing_in + (delta * rot)}

def fix_vectors(vecs, lengths, delta, rot):
    '''
    Given the passed data, fill in any missing vectors
    '''
    rad_vec = vecs['Radius']
    tan_vec = vecs['Tangent']
    mid_vec = vecs['Middle']

    _delta = 0.0

    print('delta - ', delta)

    if tan_vec[0] and not rad_vec[0]:
        rad_vec[0] = Support.get_ortho(tan_vec[0], -1 * rot).multiply(lengths[0])

    if tan_vec[1] and not rad_vec[1]:
        rad_vec[1] = Support.get_ortho(tan_vec[1], -1 * rot).multiply(lengths[0])

    print('ortho rad vec = ', rad_vec)

    if mid_vec:
        _delta = Support.get_bearing(mid_vec)
    elif rad_vec[0]:
        _delta = Support.get_bearing(rad_vec[0]) + rot * (delta / 2.0)
    elif rad_vec[1]:
        _delta = Support.get_bearing(rad_vec[1]) - rot * (delta / 2.0)
    elif tan_vec[0]:
        _delta = Support.get_bearing(tan_vec[0]) - rot * (math.pi - delta) / 2.0
    elif tan_vec[1]:
        _delta = Support.get_bearing(tan_vec[1]) + rot * (math.pi + delta) / 2.0

    print ('mo_delta = ', _delta, '\nrot = ', rot)

    if not rad_vec[0]:
        _d = _delta - rot * delta / 2.0
        rad_vec[0] = App.Vector(math.sin(_d),
                                math.cos(_d)).multiply(lengths[0])

    if not rad_vec[1]:
        _d = _delta + rot * delta / 2.0
        rad_vec[1] = App.Vector(math.sin(_d),
                                math.cos(_d)).multiply(lengths[0])

    if not tan_vec[0]:
        _d = _delta - rot * ((delta - math.pi) / 2.0)
        tan_vec[0] = App.Vector(math.sin(_d),
                                math.cos(_d)).multiply(lengths[1])

    if not tan_vec[1]:
        _d = _delta + rot * ((delta + math.pi) / 2.0)
        tan_vec[1] = App.Vector(math.sin(_d),
                                math.cos(_d)).multiply(lengths[1])

    middle_vec = vecs.get('Middle')

    if not middle_vec:
        middle_vec = App.Vector(math.sin(_delta), math.cos(_delta)).multiply(rot)

    return {'Radius': rad_vec, 'Tangent': tan_vec, 'Middle': middle_vec}

def calc_coordinates(arc, vecs, lengths):
    '''
    Calculate the coordinates (if undefined) for the arc
    '''

    _start = arc['Start']
    _center = arc['Center']
    _end = arc['End']
    _pi = arc['PI']

    undefined_coords = True

    while undefined_coords:

        if _start:
            _pi = _start.add(App.Vector(vecs['Tangent'][0]))
            _center = _start.sub(App.Vector(vecs['Radius'][0]))

        if _center:
            _start = _center.add(App.Vector(vecs['Radius'][0]))
            _end = _center.add(App.Vector(vecs['Radius'][1]))

        if _end:
            _pi = _end.sub(App.Vector(vecs['Tangent'][1]))
            _center = _end.sub(App.Vector(vecs['Radius'][1]))

        if _pi:
            _start = _pi.sub(App.Vector(vecs['Tangent'][0]))
            _end = _pi.add(App.Vector(vecs['Tangent'][1]))

        undefined_coords = not all([_start, _end, _center, _pi])

    if arc['Start']:
        if Support.within_tolerance(_start.Length, arc['Start'].Length):
            _start = arc['Start']

    if arc['End']:
        if Support.within_tolerance(_end.Length, arc['End'].Length):
            _end = arc['End']

    if arc['Center']:
        if Support.within_tolerance(_center.Length, arc['Center'].Length):
            _center = arc['Center']

    if arc['PI']:
        if Support.within_tolerance(_pi.Length, arc['PI'].Length):
            _pi = arc['PI']

    return [_start, _end, _center, _pi]

def middle_chord_check(arc, vecs):
    '''
    Test for middle / chord-only vectors and
    convert to radius / tangent vectors
    '''

    delta = arc.get('Delta')
    rot = arc.get('Direction')

    if not delta:
        return None

    delta = math.radians(delta)

    radius = arc.get('Radius')
    tangent = arc.get('Tangent')

    if radius and not tangent:
        tangent = radius * math.tan(delta / 2.0)

    elif tangent and not radius:
        radius = tangent / math.tan(delta / 2.0)

    if any(vecs['Radius']) or any(vecs['Tangent']):
        return vecs

    if vecs['Chord']:
        angle = Support.get_bearing(vecs['Chord']) - (rot * delta / 2.0)
        
        vecs['Tangent'][0] = App.Vector(math.sin(angle), math.cos(angle)).multiply(tangent)
        vecs['Radius'][0] = Support.get_ortho(vecs['Tangent'][0], -1 * rot).multiply(radius)

    if vecs['Middle']:
        angle = Support.get_bearing(vecs['Middle']) - (rot * delta / 2.0)
        vecs['Radius'][0] = App.Vector(math.sin(angle), math.cos(angle)).multiply(radius)
        vecs['Tangent'][0] = Support.get_ortho(vecs['Radius'][0], rot).multiply(tangent)

    return vecs

def ensure_minimum_parameters(arc, vecs):
    '''
    Ensure at least one vector is defined (preferrably middle ordinate)
    '''

    #filter the chord / middle vectors
    _vecs = [_v for _i, _v in vecs.items() if _v]

    #filter the radius / tangent vectors (lists within a lsit)
    #if there's something left, we have a vector - we're done
    if [_v for _group in _vecs for _v in _group if _v]:
        return vecs

    radius = arc.get('Radius')
    bearings = [arc.get('BearingIn'), arc.get('BearingOut')]
    rot = arc.get['Direction']
    delta = math.radians(arc.get('Delta'))

    #radius is a requriement
    if not radius:
        return None

    #zero or None rotation can be fixed if both bearings are known
    if not rot:

        if not all(bearings):
            return None

        rot = bearings[1] - bearings[0]
        rot /= abs(rot)

    #need at least a delta and bearing or two bearings
    if not (all(bearings) or (any(bearings) and delta)):
        return None

    if all(bearings) and not delta:
        delta = rot * (bearings[1] - bearings[0])

    elif delta and bearings[0]:
        bearings[1] = rot * (bearings[0] + delta)

    else:
        bearings[0] = rot * (bearings[1] - delta)

    #with a valid delta, rotation, and two bearings, we can compute some vectors
    result = {'Tangent': [], 'Radius': [], 'Chord': [], 'Middle': []}

    result['Tangent'] = Support.vector_from_angle(bearings)
    result['Middle'] = rot * Support.vector_from_angle(bearings[0] - ((math.pi - delta) / 2.0))
    result['Chord'] = rot * Support.vector_from_angle(bearings[0] + (delta / 2.0))

def get_lengths(arc, mat):
    '''
    Get needed parameters for arc calculation
    from the user-defined arc and the calculated vector matrix
    '''

    #[0,1] = Radius; [2, 3] = Tangent, [4] = Middle, [5] = Chord
    lengths = mat.diagonal().A[0]

    params = [arc.get('Radius'), arc.get('Tangent'), arc.get('Middle'),
              arc.get('Chord'), arc.get('Delta')]

    for _i in range(0, 2):

        #get two consecutive elements, saving only if they're valid
        _s = [_v for _v in lengths[_i*2:(_i+1)*2] if _v]

        #skip the rest if not defined, we'll use the user values
        if not _s:
            continue

        #if both were calculated and they aren't the same, quit
        if all(_s) and not Support.within_tolerance(_s):
            return None

        if _s[0] and Support.within_tolerance(_s[0], params[_i]):
            continue

        params[_i] = _s[0]

    #test middle and chord, if no user-defined value or out-of-tolerance, use calculated
    for _i in range(4, 6):

        if lengths[_i] and Support.within_tolerance(lengths[_i], params[_i - 2]):
            continue

        params[_i - 2] = lengths[_i]

    return {'Radius': params[0],
            'Tangent': params[1],
            'Chord': params[3]}

def get_delta(arc, mat):
    '''
    Get the delta value from the matrix, if possible,
    Default to the user-provided parameter if no calculated
    or values within tolerance
    '''
    delta = arc.get('Delta')

    #find the first occurence of the delta value
    for _i in range(1, 6):
        for _j in range(0, _i):
            if mat.A[_i][_j]:
                delta = mat.A[_i][_j]
                break

    if not delta:
        return None

    return {'Delta':delta}

def get_rotation(arc, vecs):
    '''
    Determine the dirction of rotation
    '''

    v1 = [_v for _v in vecs[0:3] if _v]
    v2 = [_v for _v in vecs[3:] if _v]

    if not (v1 or v2):
        return {'Direction': arc.get('Direction')}

    return {'Direction': Support.get_rotation(v1, v2)}

def calc_arc_parameters(arc):

    #Vector order:
    #Radius in / out, Tangent in / out, Middle, and Chord
    points = [arc.get('Start'), arc.get('End'),
              arc.get['Center'], arc.get('PI')]

    point_count = len([_v for _v in points if _v])

    #define the curve start at the origin if none is provided
    if point_count == 0:
        points[0] = App.Vector()

    vecs = [Support.safe_sub(arc.get('Start'), arc.get('Center'), True),
            Support.safe_sub(arc.get('End'), arc.get('Center'), True),
            Support.safe_sub(arc.get('PI'), arc.get('Start'), True),
            Support.safe_sub(arc.get('End'), arc.get('PI'), True),
            Support.safe_sub(arc.get('PI'), arc.get('Center'), True),
            Support.safe_sub(arc.get('End'), arc.get('Start'), True)
           ]

    mat = calc_scalar_matrix(vecs)

    print('\n<---- Matrix ---->\n', mat)

    result = get_lengths(arc, mat)

    result.update(get_delta(arc, mat))

    if not result['Delta']:
        print('Invalid curve definition: cannot determine central angle')
        return None

    #compute the rotation direction of the arc
    result.update(get_rotation(arc, vecs))

    #compute the bearing using the last row of the matrix and the delta / rotation values
    result.update(get_bearing(arc, mat, result['Delta'], result['Direction']))

    print('\n<---- Arc ---->\n', result)

    if not result['Direction']:
        print('Invalid curve definition: cannot determine curve direction')
        return None

    if not result['BearingIn']:
        print('Invalid curve definition: cannot determine curve bearings')
        return None

    #validate the delta
    rot, delta = calc_delta(arc, vecs)

    print ('\n<---- Rotation ---->\n', rot)
    print ('\n<---- Delta ---->\n', delta)

    if not (delta and rot):
        print('Invalid curve definition: Cannot compute central angle')
        return None

    lengths = calc_lengths(arc, vecs, delta)

    print('\n<---- Radius / Tangent ---->\n', lengths)

    if not lengths:
        print('Invalid curve definition: Cannot compute tangent or radius lengths')
        return None

    vecs = fix_vectors(vecs, lengths, delta, rot)

    print ('\n<---- Fixed Vectors ---->\n', vecs)

    #calculate the bearings - returns a list of four values
    #first two - start bearing, last two - end bearing
    bearings = calc_bearings(arc, vecs)

    print ('\n<---- Bearings ---->\n', bearings)

    if not bearings:
        print ('Invalid curve definition')
        return None

    radius = lengths[0]
    half_delta = delta / 2.0

    coords = calc_coordinates(arc, vecs, lengths)

    print('\n<---- Coordinates ---->\n', coords)
    #scale_factor = 1.0 / Units.scale_factor()

    print('\n\n')
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
        'Start': coords[0],
        'Center': coords[2],
        'End': coords[1],
        'PI': coords[3]
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
#Radius vectors:  [Vector (-508.7011218152017, -436.03115561156324, 0.0), Vector (10.728516713741602, -669.914098171641, 0.0)] 

#Tangent vectors:  [Vector (204.79088342927093, -238.92180821776492, -0.0), Vector (314.63875509967215, 5.038865657687206, 0.0)] 

#Middle vector:  Vector (-303.9102383859307, -674.9529638293282, 0.0)
#bearings:  [2.4329645426705673, 1.5547829309078485]

#{'Direction': -1.0, 'Delta': 50.3161, 'Radius': 670.0, 'Length': 588.3816798810216, 'Tangent': 314.67910063712156, 'Chord': 569.6563702820052, 'External': 70.21816809491217, 'MiddleOrd': 63.55717091445238, 'BearingIn': 139.3986, 'BearingOut': 89.0825, 'Start': Vector (400.44639227036157, -467.1857190779628, 0.0), 'Center': Vector (909.1475140855633, -31.154563466399697, 0.0), 'End': Vector (919.8760307993049, -701.0686616380407, 0.0), 'PI': Vector (605.2372756996326, -706.1075272957279, 0.0)}

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
