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

from transportationwb.ScriptedObjectSupport import Units

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

def calc_arc_parameters(points):
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
        'Radius': radius, 'Delta': angle, 'Direction': clock_dir, 'BearingIn': bearing_in,
        'BearingOut': bearing_out
    }

def get_points(arc_dict, interval, interval_type='Segment'):
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

    Points are returned references to (0.0, 0.0, 0.0)
    '''

    angle = arc_dict['Delta']
    direction = arc_dict['Direction']
    bearing = arc_dict['BearingIn']
    radius = arc_dict['Radius']

    #validate paramters
    if not direction:
        return None

    if radius <= 0.0:
        return None

    if angke <= 0.0:
        return None

    if interval <= 0:
        return None

    if not 0.0 < bearing < math.pi * 2.0:
        return None

    scale_factor = Units.scale_factor()

    _forward = App.Vector(math.sin(bearing), math.cos(bearing), 0.0)
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

        result.append(_dfw.add(_drt).multiply(radius_mm))

    return result
