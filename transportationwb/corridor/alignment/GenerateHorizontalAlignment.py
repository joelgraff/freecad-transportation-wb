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

import FreeCAD as App
import FreeCADGui as Gui
import os
import math
import Part
import Draft
from PySide import QtGui
from PySide import QtCore
from transportationwb.corridor.alignment import HorizontalCurve, Metadata

class GenerateHorizontalAlignment():

    dms_to_deg = staticmethod(lambda _x: _x[0] + _x[1] / 60.0 + _x[2] / 3600.0)

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Shift+H",
                'MenuText': "Generate Horizontal Alignment",
                'ToolTip' : "Generate the Horizontal Alignment from an Alignment group",
                'CmdType' : "ForEdit"}

    def _azimuth_from_bearing(self, angle, quadrant):
        '''
        Calculate the azimuth from true bearing.
        Angle - bearing angle in radians
        Quadrant - Quadrant of bearing ('NE', 'NW', 'SE', 'SW')
        '''

        #1st quadrnat
        result = angle

        if quadrant == 'NW': #4th quadrant
            result = (2.0 * math.pi) - angle

        elif quadrant == 'SW': #3rd quadrant
            result = math.pi + angle

        elif quadrant == 'SE': #2nd quadrant
            result = math.pi - angle

        return result

    def _project_arc(self, point, curve, azimuth, segments=4):
        '''
        Return a series of points along an arc based on the starting point,
        central angle (delta) and radius
        '''

        #calculate the circle center from the passed point and bearing
        #use the circle center with the delta to generate the remaining points along the arc

        points = []

        curve_dir = 1.0

        if curve.Direction == 'L':
            curve_dir = -1.0

        if curve.Bearing != 0.0:
            azimuth = self._azimuth_from_bearing(math.radians(curve.Bearing), curve.Quadrant)

        #adjust bearing to reflect true north = pi / 2 radians
        #cur_bearing += math.radians(90.0)

        #print ('----> Ajusted Bearing: ', cur_azimuth)
        central_angle = math.radians(curve.Delta)

        angle_seg = central_angle / float(segments)
        radius = float(curve.Radius)

        cur_point = App.Vector(point)

        fx = math.sin(azimuth)
        fy = math.cos(azimuth)

        lx = -math.cos(azimuth)
        ly = math.sin(azimuth)

        print('direction: ', curve_dir)
        print('azimuth: ', azimuth)
        print('fx: ', fx)
        print('fy: ', fy)
        print('lx: ', lx)
        print('ly: ', ly)

        for _i in range(0, segments):

            print('\n--Segment: ', _i)

            delta = float(_i + 1) * angle_seg

            f_dist = radius * math.sin(delta)

            fdx = f_dist * fx
            fdy = f_dist * fy

            print('f_dx: ', fdx)
            print('f_dy: ', fdy)

            l_dist = radius * (1 - math.cos(delta))

            ldx = l_dist * (-lx) * curve_dir
            ldy = l_dist * (-ly) * curve_dir

            print('l_dx: ', ldx)
            print('l_dy: ', ldy)

            print('point: ', cur_point)
            print('dx: ', fdx + ldx)
            print('dy: ', fdy + ldy)

            print('azimuth: ', azimuth)

            cur_point.x = point.x + fdx + ldx
            cur_point.y = point.y + fdy + ldy

            points.append(cur_point)

            #if _i == 0:

                #cur_point = App.Vector()

                #_delta = 25.0 / radius

                #_fdx = radius * math.sin(_delta) * fx
                #_fdy = radius * math.sin(_delta) * fy
                #_ldx = radius * (1 - math.cos(_delta)) * (-lx) * curve_dir
                #_ldy = radius * (1 - math.cos(_delta)) * (-ly) * curve_dir

                #cur_point.x = point.x + _fdx + _ldx
                #cur_point.y = point.y + _fdy + _ldy

                #points.append(cur_point)

            #elif _i == segments - 2:

                #cur_point = App.Vector()

                #_delta = ((central_angle * radius) - 25) / radius

                #_fdx = radius * math.sin(_delta) * fx
                #_fdy = radius * math.sin(_delta) * fy
                #_ldx = radius * (1 - math.cos(_delta)) * (-lx) * curve_dir
                #_ldy = radius * (1 - math.cos(_delta)) * (-ly) * curve_dir

                #cur_point.x = point.x + _fdx + _ldx
                #cur_point.y = point.y + _fdy + _ldy

                #points.append(cur_point)

            cur_point = App.Vector()

        print ('\nGenerated arc points: ', points)

        azimuth += central_angle * curve_dir

        if azimuth < 0:
            azimuth += 360.0

        elif azimuth > 360.0:
            azimuth -= 360.0

        return points, azimuth

    def _project_line(self, point, azimuth, distance, segments=4):
        '''
        Project a given distance along a line in the X,Y plane from a given cartesion coordinate
        '''

        f_segs = float(segments)

        interval = distance / f_segs
        cos_az = math.cos(azimuth)
        sin_az = math.sin(azimuth)
        _dy = interval * cos_az
        _dx = interval * sin_az

        _x = point[0]
        _y = point[1]

        result = []

        print('building line: ', _x, _y, _dx, _dy, interval)

        offsets = []

        for _i in range(1, segments + 1):

            offsets.append([_dx * _i, _dy * _i])

            #second point is an anchor point
           # if _i == 1:
           #     offsets.append([25.0 * sin_az, 25.0 * cos_az])

            #elif _i == segments - 1:
            #    offsets.append([((interval * (_i + 1)) - 25.0) * sin_az, ((interval * (_i + 1)) - 25.0) * cos_az])

        for _i in range(0, len(offsets)):

            result.append(App.Vector(_x + offsets[_i][0], _y + offsets[_i][1], 0.0))

        print('line points: ', result)
        return result

    def sort_key(self, item):
        return item.Label

    def generate_spline(self, points, label):
        '''
        Generate a spline based on passed points
        '''

        obj_type = "BSpline"

        pt_count = len(points)

        if pt_count < 2:
            return None

        elif len(points) == 2: 
            obj_type = "Line"

        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", label)

        Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = points
        obj.Support = None
        obj.Label = label

        Draft._ViewProviderWire(obj.ViewObject)

        return obj

    def _get_station_distance(self, station, meta):
        '''
        Returns the distance in feet along an alignment that a station represents,
        adjusting for station equations
        '''

        eq_name = 'Equation_1'
        eq_no = 1
        eq_list = []

        while eq_name in meta.PropertiesList:

            eq_list.append(meta.getPropertyByName(eq_name))

            eq_no += 1
            eq_name = 'Equation_' + str(eq_no)

        if eq_list == []:
            return -1.0

        dist_acc = 0.0

        start_station = meta.Start_Station.Value

        print(eq_list)
        print('start: ', start_station)
        print('target: ', station)

        prev_eq_fwd = start_station

        for eq in eq_list:

            eq_back = eq[0] * 25.4 * 12.0

            if prev_eq_fwd <= station <= eq_back:
                return dist_acc + station - prev_eq_fwd

            #increment distance accumulator
            dist_acc += eq_back - prev_eq_fwd

            prev_eq_fwd = eq[1] * 25.4 * 12.0

        #final test for the last station equation to the end station
        eq_back = meta.End_Station.Value

        if prev_eq_fwd <= station <= eq_back:
            return dist_acc + station - prev_eq_fwd

        return -1.0

    def _get_reference_coordinates(self, alignment, station):
        '''
        Return the x,y,z coordiantes of a station along the specified alignment
        '''

        spline = App.ActiveDocument.getObject('HA_' + alignment)
        parent_meta = App.ActiveDocument.getObject(alignment + '_metadata')

        if spline is None:
            print('Reference spline not found: ', 'HA_' + alignment)
            return None

        distance = self._get_station_distance(station, parent_meta)

        if distance < 0.0:
            print('invalid station')
            return None

        print('discretize ', distance, spline.Name)

        result = spline.Shape.discretize(Distance=distance)[1]

        if len(result) < 2:
            print('failed discretize')
            return None

        print('coordinates: ', result)
        return result

    def build_alignment(self, alignment):
        '''
        Generate the horizontal alignment
        '''

        meta = None
        curves = None

        for item in alignment.InList[0].OutList:
            if 'metadata' in item.Label:
                meta = item
            
            if 'Horizontal' in item.Label:
                curves = item

        if meta is None:
            print('Alignment metadata not found')
            return

        if curves is None:
            print('Horizontal curve data not found')
            return

        #calculate the azimuth from bearing and direciton
        azimuth = self._azimuth_from_bearing(math.radians(meta.Bearing), meta.Quadrant)

        cur_pt = meta.Start_Station.Value
        next_pc = 0.0

        cur_point = App.Vector(0.0, 0.0, 0.0)
        ref_point = None

        if meta.Alignment != '':
            print('getting reference alignment...')
            ref_point = self._get_reference_coordinates(meta.Alignment, meta.Primary.Value)

            if ref_point is None:
                print("Invalid reference alignment")
                return

        points = [cur_point]

        #curves.OutList.sort(key=self.sort_key)

        App.ActiveDocument.recompute()
        last_curve = None

        for curve in curves.OutList:

            next_pc = curve.PC_Station.Value
            new_points = []
            length = 0.0

            #if the PT and the PC are within an inch, ignore the error
            if next_pc - cur_pt > 25.4:

                if curve.Bearing != []:
                    azimuth = self._azimuth_from_bearing(math.radians(curve.Bearing), curve.Quadrant)
                else:
                    print('NULL BEARING')

                print('-------PROJECTING LINE------')
                print('point: ', cur_point)
                print('azimuth: ', azimuth)
                print('distance: ', next_pc - cur_pt)
                
                new_points.extend(self._project_line(cur_point, azimuth, next_pc - cur_pt))
                cur_point = new_points[len(new_points) - 1]

            print('---------PROJECTING ARC--------')
            print('Label: ', curve.Label)
            print('Point: ', cur_point)
            print('Azimuth: ', azimuth)
            print('Radius: ', curve.Radius)
            print('Delta: ', curve.Delta)

            arc_points, azimuth = self._project_arc(cur_point, curve, azimuth)

            print('Adding points to list: ', new_points, arc_points)

            points.extend(new_points)
            points.extend(arc_points)

            cur_pt = curve.PC_Station.Value + (curve.Radius.Value * math.radians(curve.Delta))
            cur_point = points[len(points) - 1]

        #if the last curve ends more than an inch from the end of the project, 
        #plot a tangent line to complete it
        if meta.End_Station.Value - cur_pt > 25.4:
            points.extend(self._project_line(cur_point, azimuth, meta.End_Station.Value - cur_pt))

        parent = curves.InList[0]
        spline = self.generate_spline(points, 'HA_' + parent.Label)

        #adjust vertices by the reference delta, if there's a reference point
        if not ref_point is None:

            #get the distance of the reference point along the secondary alignment
            ref_dist = meta.Secondary.Value - meta.Start_Station.Value

            #discretize the spline to get the cartesian coordinate
            #and subtract it from the starting point to get the deltas
            ref_delta = points[0].sub(spline.discretize(distance = ref_dist)[1])

            #adjust the alginment points by the deltas
            for _x in range(0, len(points)):
                points[_x] =  points[_x].add(ref_delta)

            #rebuild the spline
            spline = self.generate_spline(points, 'HA_' + parent.Label)
            
        parent.addObject(spline)

        App.ActiveDocument.recompute()

    def validate_selection(self, grp):
        '''
        Validate the selected object as either a horizontal group or 
        an alignment group that contains a horizontal group.
        '''

        if grp.TypeId != 'App::DocumentObjectGroup':
            return None

        if 'Horizontal' in grp.Label:
            return grp

        for item in grp.OutList:
            if 'Horizontal' in item.Label:
                return item
        
        return None

    def Activated(self):
        '''
        Generate the horizontal alignment
        '''

        group = self.validate_selection(Gui.Selection.getSelection()[0])

        if group is None:
            print('Horizontal curve group or an alignment group containing a horizontal curve group not selected')
            return

        print('generating alignment for ', group.Label)
        self.build_alignment(group)

Gui.addCommand('GenerateHorizontalAlignment', GenerateHorizontalAlignment())