'''
Vertical alignment generation tool for creating parabolic vertical curves
'''
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

import os
import math

import FreeCAD as App
import FreeCADGui as Gui
import Draft

class GenerateVerticalAlignment():
    '''
    Vertical alignment generation class.
    Builds a spline based on a selected group of Vertical curve objects
    '''
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
                'Accel'   : "Alt+G",
                'MenuText': "Generate Vertical Alignment",
                'ToolTip' : "Generate the Vertical Alignment from an Alignment group",
                'CmdType' : "ForEdit"}

    def _get_azimuth(self, angle, quadrant):
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
        two_pi = math.pi * 2.0

        if curve.Direction == 'L':
            curve_dir = -1.0

        if curve.Bearing != 0.0:
            azimuth = self._get_azimuth(math.radians(curve.Bearing), curve.Quadrant)

        central_angle = math.radians(curve.Delta)

        angle_seg = central_angle / float(segments)
        radius = float(curve.Radius)

        _fw = App.Vector(math.sin(azimuth), math.cos(azimuth), 0.0)
        _lt = App.Vector(-_fw.y, _fw.x, 0.0)

        for _i in range(0, segments):

            delta = float(_i + 1) * angle_seg

            fw_delta = App.Vector(_fw).multiply(radius * math.sin(delta))
            lt_delta = App.Vector(-_lt).multiply(curve_dir * radius * (1 - math.cos(delta)))

            points.append(point.add(fw_delta).add(lt_delta))

        azimuth += central_angle * curve_dir

        if azimuth > two_pi:
            azimuth -= two_pi

        elif azimuth < 0.0:
            azimuth += two_pi

        return points, azimuth

    def _project_line(self, point, azimuth, distance, segments=4):
        '''
        Project a given distance along a line in the X,Y plane from a given cartesion coordinate
        '''

        #pre-calculate the delta-x / delta-y values for projection
        _delta = App.Vector(math.sin(azimuth), math.cos(azimuth))
        _delta.multiply(distance / float(segments))

        result = []

        #create line points for the start / end of each segment
        for _i in range(1, segments + 1):
            result.append(App.Vector(point[0] + _delta.x * _i, point[1] + _delta.y * _i, 0.0))

        return result

    def generate_spline(self, points, label):
        '''
        Generate a spline based on passed points
        '''

        pt_count = len(points)

        if pt_count < 2:
            return None

        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", label)

        Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = points
        obj.Support = None
        obj.Label = label

        Draft._ViewProviderWire(obj.ViewObject)

        return obj

    def _get_global_sta(self, local_sta, meta):
        '''
        Convert a station to a generic, zero-based global station
        independent of alignment station equations.
        This is equivalent to the distance along an alignment
        from the start station provided by the metadata objecet
        '''

        eq_name = 'Equation_1'
        eq_no = 1
        eq_list = []

        while eq_name in meta.PropertiesList:

            eq_list.append(meta.getPropertyByName(eq_name))
            eq_no += 1

            eq_name = 'Equation_' + str(eq_no)

        fwd_sta = meta.Start_Station.Value
        end_sta = meta.End_Station.Value
        offset = 0

        for st_eq in eq_list:

            bck_sta = st_eq[0] * 304.8

            if fwd_sta <= local_sta <= bck_sta:
                return  (local_sta - fwd_sta) + offset

            offset += (bck_sta - fwd_sta)
            fwd_sta = st_eq[1] * 304.8

        #if we're still here, the value hasn't been located.
        #final test between the last forward station and the end
        if fwd_sta <= local_sta <= end_sta:
            return (local_sta - fwd_sta) + offset

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

        distance = self._get_global_sta(station, parent_meta)

        if distance < 0.0:
            print('invalid station')
            return None

        result = spline.Shape.discretize(Distance=distance)[1]

        if len(result) < 2:
            print('failed to discretize')
            return None

        return result

    def build_alignment(self, alignment):
        '''
        Generate the Vertical alignment
        '''

        meta = None
        curves = None

        for item in alignment.InList[0].OutList:

            if 'metadata' in item.Label:
                meta = item

            if 'Vertical' in item.Label:
                curves = item

        if meta is None:
            print('Alignment metadata not found')
            return

        if curves is None:
            print('Vertical curve data not found')
            return

        cur_pt = self._get_global_sta(meta.Start_Station.Value, meta)

        if cur_pt == -1:
            print("unable to convert station ", meta.Start_Station, "to global stationing")
            return

        next_pc = 0.0
        cur_point = App.Vector(0.0, 0.0, 0.0)

        points = [cur_point]

        App.ActiveDocument.recompute()

        for curve in curves.OutList:

            next_pc = self._get_global_sta(curve.PC_Station.Value, meta)

            if next_pc == -1:
                print('unable to convert station ', next_pc, ' to global stationing...')
                return

            new_points = []

            print('---------PROJECTING ARC--------')
            print('Label: ', curve.Label)
            print('Point: ', cur_point)
#            print('Azimuth: ', azimuth)
            print('Radius: ', curve.Radius)
            print('Delta: ', curve.Delta)

            arc_points, azimuth = self._project_arc(cur_point, curve, azimuth)

            points.extend(new_points)
            points.extend(arc_points)

            cur_pt = self._get_global_sta(curve.PC_Station.Value, meta)
            cur_pt += curve.Radius.Value * math.radians(curve.Delta)

            cur_point = points[len(points) - 1]

        #if the last curve ends more than an inch from the end of the project,
        #plot a tangent line to complete it
        remainder = self._get_global_sta(meta.End_Station.Value, meta) - cur_pt

        if remainder > 25.4:
            points.extend(self._project_line(cur_point, azimuth, remainder))

        parent = curves.InList[0]

        spline_name = 'HA_' + parent.Label

        if not App.ActiveDocument.getObject(spline_name) is None:
            App.ActiveDocument.removeObject(spline_name)

        spline = self.generate_spline(points, spline_name)

        App.ActiveDocument.recompute()

        #adjust vertices by the reference delta, if there's a reference point
        ref_point = None

        if meta.Alignment != '':
            print('getting reference alignment...')
            ref_point = self._get_reference_coordinates(meta.Alignment, meta.Primary.Value)

            if ref_point is None:
                print("Invalid reference alignment")
                return

        if not ref_point is None:

            #get the distance of the reference point along the secondary alignment
            #first converting to global stationing
            side_position = self._get_global_sta(meta.Secondary.Value, meta)
            side_start_sta = self._get_global_sta(meta.Start_Station.Value, meta)

            ref_dist = side_position - side_start_sta
            ref_delta = ref_point

            #discretize the spline to get the cartesian coordinate of the reference point
            #and subtract it from the starting point to get the deltas
            if ref_dist > 0.0:
                ref_coord = spline.Shape.discretize(Distance=ref_dist)[1]
                ref_delta = ref_delta.add(points[0].sub(ref_coord))

            #adjust the alginment points by the deltas
            for _x in range(0, len(points)):
                points[_x] = points[_x].add(ref_delta)

            #rebuild the spline
            spline = self.generate_spline(points, spline_name)

        parent.addObject(spline)

        App.ActiveDocument.recompute()

    def validate_selection(self, grp):
        '''
        Validate the selected object as either a Vertical group or
        an alignment group that contains a Vertical group.
        '''

        if grp.TypeId != 'App::DocumentObjectGroup':
            return None

        if 'Vertical' in grp.Label:
            return grp

        for item in grp.OutList:
            if 'Vertical' in item.Label:
                return item

        return None

    def Activated(self):
        '''
        Generate the Vertical alignment
        '''

        group = self.validate_selection(Gui.Selection.getSelection()[0])

        if group is None:
            print('Valid Vertical curve group not found')
            return

        print('generating alignment for ', group.Label)
        self.build_alignment(group)

Gui.addCommand('GenerateVerticalAlignment', GenerateVerticalAlignment())
