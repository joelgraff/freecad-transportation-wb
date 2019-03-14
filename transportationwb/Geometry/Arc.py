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
import time

def gen_arc():

    start = time.time()

    bearing = math.radians(45)
    delta = math.radians(27)
    start_vec = App.Vector()

    for i in range(0, 500):
        Draft.makeWire(discretize_arc(start_vec, bearing, 100, delta, 1000, 'Segment'))

    print ('discretize_arc: ', time.time() - start)

    pl = App.Placement()
    pl.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
    pl.Base = (21689.728516, -21912.738281, 0.0)

    circle = Draft.makeCircle(radius=30480, placement = pl, startangle=-252.0, endangle=-225.0)

    start = time.time()

    for i in range(0, 500):

        Draft.makeWire(circle.Shape.discretize(Number=1000))

    print('draft.makewire: ', time.time() - start)
def calc_angle_increment(central_angle, radius, interval, interval_type):
    '''
    Calculate the radian increment for the specified
    subdivision method
    '''

    if central_angle == 0.0:
        return 0.0

    if interval <= 0.0:
        print('Invalid interval value', interval, 'for interval type ', interval_type)
        return 0.0

    if interval_type == 'Segment':
        return central_angle / interval

    if interval_type == 'Interval':
        return interval / radius

    if interval_type == 'Tolerance':
        return 2 * math.acos(1 - (interval / radius))

    return 0.0
    
def discretize_arc(start_coord, bearing, radius, angle, interval, interval_type):
    '''
    Discretize an arc into the specified segments.
    Resulting list of coordinates omits provided starting point and concludes with end point

    Radius in feet
    Central Angle in radians
    bearing - angle from true north of starting tangent of arc
    segments - number of evenly-spaced segments to subdivide arc
    interval - fixed length foreach arc subdivision
    interval_type - one of three options:
        'segment' - subdivide the curve into n equal segments
        'fixed' - subdivide the curve into segments of fixed length
        'tolerance' - subdivide the curve, minimizing the error between the segment and curve at or below the tolerance value
    '''

    _forward = App.Vector(math.sin(bearing), math.cos(bearing), 0.0)
    _right = App.Vector(_forward.y, -_forward.x, 0.0)
    
    partial_segment = False

    curve_dir = 1.0

    if angle < 0.0:
        curve_dir = -1.0
        angle = abs(angle)

    seg_rad = calc_angle_increment(angle, radius, interval, interval_type)

    segments = 1

    if angle != 0.0:
        segments = int(angle / seg_rad)

    #partial segments where the remainder angle creates a curve longer than one ten-thousandth of a foot.
    partial_segment = (abs(seg_rad * float(segments) - angle) * radius > 0.0001)

    radius_mm = radius * 304.80

    result = []

    for _i in range(0, int(segments)):
        
        delta = float(_i + 1) * seg_rad

        _dfw = App.Vector(_forward)
        _drt = App.Vector()

        if delta != 0.0:

            _dfw.multiply(math.sin(delta))
            _drt = App.Vector(_right).multiply(curve_dir * (1 - math.cos(delta)))

        result.append(start_coord.add(_dfw.add(_drt).multiply(radius_mm)))

    #remainder of distance must be greater than one ten-thousandth of a foot
    if partial_segment:

        _dfw = _forward.multiply(math.sin(angle))
        _drt = App.Vector(_right).multiply(curve_dir * (1 - math.cos(angle)))

        result.append(start_coord.add(_dfw.add(_drt).multiply(radius_mm)))

    return result