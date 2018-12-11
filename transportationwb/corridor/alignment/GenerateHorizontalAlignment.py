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

    def _project_arc(self, point, curve, bearing, segments=4):
        '''
        Return a series of points along an arc based on the starting point,
        central angle (delta) and radius
        '''

        #calculate the circle center from the passed point and bearing
        #use the circle center with the delta to generate the remaining points along the arc

        points = []

        cur_bearing = bearing

        if curve.Bearing != []:
            cur_bearing = math.radians(curve.Bearing)

        #adjust bearing to reflect true north = pi / 2 radians
        cur_bearing += math.radians(90.0)

        print ('----> Ajusted Bearing: ', cur_bearing)
        central_angle = math.radians(curve.Delta)

        if curve.Direction == 'L':
            central_angle *= -1

        delta = central_angle / float(segments)
        radius = float(curve.Radius)

        cur_point = App.Vector(point)

        fx = math.cos(cur_bearing)
        fy = math.sin(cur_bearing)

        lx = -math.sin(cur_bearing)
        ly = math.cos(cur_bearing)

        for _i in range(0, segments):

            dx = cur_point.x
            dy = cur_point.y

            print('project arc point: ', cur_point, dx, dy, cur_bearing)

            dx += radius * math.sin(delta) * fx
            dy += radius * math.sin(delta) * fy

            dx += radius * (1 - math.cos(delta)) * (-lx)
            dy += radius * (1 - math.cos(delta)) * (-ly)

            cur_point.x = dx
            cur_point.y = dy

            points.append(cur_point)

            cur_bearing -= delta
            cur_point = App.Vector(cur_point)

        print ('Generated arc points: ', points)

        return points, cur_bearing - math.radians(90.0)

    def _azimuth_from_bearing(self, angle, quadrant):
        '''
        Calculate the azimuth from true bearing.
        Angle - bearing angle in radians
        Quadrant - Quadrant of bearing ('NE', 'NW', 'SE', 'SW')
        '''

        #default is the NE case
        result = angle

        if quadrant == 'NW':
            result = math.pi - angle

        elif quadrant == 'SW':
            result = (math.pi / 2.0) + angle

        elif quadrant == 'SE':
            result = (math.pi / 2.0) - angle

        return result

    def _project_line(self, point, bearing, distance, segments=4):
        '''
        Project a given distance along a line in the X,Y plane from a given cartesion coordinate
        '''

        f_segs = float(segments)

        _dy = distance * math.cos(bearing) / f_segs
        _dx = distance * math.sin(bearing) / f_segs

        _x = point[0]
        _y = point[1]

        result = []

        print('building line: ', _x, _y, _dx, _dy, segments)

        for _i in range(1, segments + 1):

            result.append(App.Vector(_x + (_dx * _i), _y + (_dy * _i), 0.0))

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

        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", obj_type)

        Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = points
        obj.Support = None
        obj.Label = label

        Draft._ViewProviderWire(obj.ViewObject)

        return obj

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

        points = [cur_point]

        #curves.OutList.sort(key=self.sort_key)

        App.ActiveDocument.recompute()

        for curve in curves.OutList:

            next_pc = curve.PC_Station.Value
            new_points = []
            length = 0.0

            #if the PT and the PC are within an inch, ignore the error
            if next_pc - cur_pt > 25.4:
                print('-------PROJECTING LINE------')

                if curve.Bearing != []:
                    azimuth = self._azimuth_from_bearing(math.radians(curve.Bearing), curve.Quadrant)
                else:
                    print('NULL BEARING')

                print('Point: ', cur_point)
                print('Azimuth: ', azimuth)
                print('Current PT: ', cur_pt)
                print('Next PC: ', next_pc)

                new_points.extend(self._project_line(cur_point, azimuth, next_pc - cur_pt))
                cur_point = new_points[len(new_points) - 1]

            print('---------PROJECTING ARC--------')
            print('Label: ', curve.Label)
            print('Point: ', cur_point)
            print('Azimuth: ', azimuth)

            arc_points, azimuth = self._project_arc(cur_point, curve, azimuth)

            print('Adding points to list: ', new_points, arc_points)

            points.extend(new_points)
            points.extend(arc_points)

            cur_pt = curve.PC_Station.Value + (curve.Radius.Value * math.radians(curve.Delta))
            cur_point = points[len(points) - 1]

        print('Spline points:')
        print(points)
        spline = self.generate_spline(points, curves.Label)

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

        print('generating alignment ', group.Label)
        self.build_alignment(group)

Gui.addCommand('GenerateHorizontalAlignment', GenerateHorizontalAlignment())