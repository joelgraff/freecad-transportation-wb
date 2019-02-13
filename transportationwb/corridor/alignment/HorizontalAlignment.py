
# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX AUTHOR_NAME <AUTHOR_EMAIL>                         *
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
Alignment object for managing 2D (Horizontal and Vertical) and 3D alignments
'''
import math

import FreeCAD as App
import Draft
import numpy

from transportationwb.ScriptedObjectSupport import Properties, Units, Utils, DocumentProperties

_CLASS_NAME = 'Alignment'
_TYPE = 'Part::Part2DObjectPython'

__title__ = _CLASS_NAME + '.py'
__author__ = "AUTHOR_NAME"
__url__ = "https://www.freecadweb.org"

meta_fields = ['ID', 'Northing', 'Easting']
data_fields = ['Northing', 'Easting', 'Bearing', 'Distance', 'Radius', 'Degree']
station_fields = ['Parent_ID', 'Back', 'Forward']

def create(data, object_name='', units='English', parent=None):
    '''
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    parent - Optional.  Reference to existing DocumentObjectGroup.  Defaults to ActiveDocument
    data - a list of the curve data in tuple('label', 'value') format
    '''

    if not data:
        print('No curve data supplied')
        return

    _obj = None
    _name = _CLASS_NAME

    if object_name:
        _name = object_name

    if parent:
        _obj = parent.newObject(_TYPE, _name)
    else:
        _obj = App.ActiveDocument.addObject(_TYPE, _name)

    result = _HorizontalAlignment(_obj)
    result.set_data(data)

    if not units == 'English':
        result.set_units(units)

    _ViewProviderHorizontalAlignment(_obj.ViewObject)

    return result

class _HorizontalAlignment():

    # Metadata headers include:
    #   ID - The ID of the alignment
    #   Parent_ID - The ID of the parent alignment (optional)
    #   Back/Forward - The dataum station for the start of the alignment, or parent / child station for intersection equations
    #   Northing / Easting - The datum planar coordinates
    #
    # Data headers include:
    #   Northing / Easting - The planar coordinates of the curve PI
    #   Bearing - The bearing of the tangent from the previous PI
    #   Distance - The distance between the current PU and the prvious PI
    #   Radius / Degree - The radius or degree of curvature for the curve
    #   Back / Forward - Station equation.  May be specified in absence of other data.
    #       Starting station defined with first PI by providing a 'forward' value.

    def __init__(self, obj, label=''):
        '''
        Main class intialization
        '''

        self.no_execute = True

        self.Type = "_" + _CLASS_NAME
        self.Object = obj
        self.errors = []

        obj.Proxy = self

        obj.Label = label

        if not label:
            obj.Label = obj.Name

        #add class properties
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'String', 'Parent ID', 'ID of alignment parent', '')
        Properties.add(obj, 'Vector', 'Intersection Equation', 'Station equation for intersections with parent alignment', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Alignment Equations', 'Station equation along the alignment', [])
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Geometry', 'Geometry defining the alignment', [])
        Properties.add(obj, 'String', 'Units', 'Alignment units', 'English', is_read_only=True)
        Properties.add(obj, 'VectorList', 'Points', 'Discretization of geometry as a list of vectors', [])
        Properties.add(obj, 'Integer', 'Segments', 'Set the curve segments to control accuracy', 1)

        delattr(self, 'no_execute')

    def __getstate__(self):
        '''
        State method for serialization
        '''
        return self.Type

    def __setstate__(self, state):
        '''
        State method for serialization
        '''
        if state:
            self.Type = state

    def set_units(self, units):
        '''
        Sets the units of the alignment
        Does not recompute values
        '''

        self.Object.Units = units

    def set_id(self, text=''):
        '''
        Sets the ID of the alignment.
        If no text / empty string is provided, ID is assigned the object label
        '''

        if not text:
            text = self.Object.label

        self.Object.ID.Value = text

    def assign_meta_data(self, data):
        '''
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        '''

        obj = self.Object

        if data['ID']:
            obj.ID = data['ID']

        if data['Northing'] and data['Easting']:
            obj.Datum = App.Vector(float(data['Easting']), float(data['Northing']), 0.0)

    def assign_station_data(self, data):
        '''
        Assign the station and intersection equation data
        '''

        obj = self.Object

        for key in data.keys():

            if key == 'equations':

                for _eqn in data['equations']:

                    back = 0
                    forward = 0

                    try:

                        if _eqn[0]:
                            back = float(_eqn[0])

                        if _eqn[1]:
                            forward = float(_eqn[1])

                    except:
                        self.errors.append('Unable to convert station equation (Back: %s, Forward: %s)' % (_eqn[0], _eqn[1]))
                        continue

                    eqns = obj.Alignment_Equations
                    eqns.append(App.Vector(back, forward, 0.0))

                    obj.Alignment_Equations = eqns

            else:

                back = data[key][0]
                forward = data[key][1]

                try:
                    back = float(back)
                    forward = float(forward)

                except:
                    self.errors.append('Unable to convert intersection equation with parent %s: (Back: %s, Forward: %s' % (key, data[key][0], data[key][1]))

                obj.Parent_ID = key
                obj.Intersection_Equation = App.Vector(back, forward, 0.0)

    def assign_geometry_data(self, datum, data):
        '''
        Iterate the dataset, extracting geometric data
        Validate data
        Create separate items for each curve / tangent
        Assign Northing / Easting datums
        '''

        _points = [datum]
        _geometry = []

        for item in data:

            _ne = []
            _db = []
            _rd = []

            try:
                _ne = [item['Northing'], item['Easting']]
                _db = [item['Distance'], item['Bearing']]
                _rd = [item['Radius'], item['Degree']]

            except:
                self.errors.append('Inivalid geometric data: %s' % item)
                continue

            geo_vector = App.Vector(0.0, 0.0, 0.0)
            point_vector = App.Vector(0.0, 0.0, 0.0)

            #parse degree of curve / radius values
            if _rd[0]:
                try:
                    geo_vector.z = float(_rd[0])
                except:
                    self.errors.append('Invalid radius: %s' % _rd[0])

            elif _rd[1]:
                try:
                    geo_vector.z = Utils.doc_to_radius(float(_rd[1]))
                except:
                    self.errors.append('Invalid degree of curve: %s' % _rd[1])
            else:
                self.errors.append('Missing Radius / Degree of Curvature')

            #parse bearing / distance values
            if any(_db) and not all(_db):
                self.errors.append('(Distance, Bearing) Incomplete: (%s, %s)' % tuple(_db))
            
            elif all(_db):
                #get the last point in the geometry for the datum, unless empty
                datum = self.Object.Datum

                try:
                    _db[0] = float(_db[0])
                    _db[1] = float(_db[1])

                except:
                    self.errors.append('(Distance, Bearing) Invalid: (%s, %s)' % tuple(_db))

                #successful conversion of distance/bearing to floats

                #set values to geo_vector, adding the previous position to the new one
                point_vector = Utils.distance_bearing_to_coordinates(_db[0], _db[1])
                geo_vector.x, geo_vector.y = _db

                if not Units.is_metric_doc():
                    point_vector.multiply(304.8)

                point_vector = _points[-1].add(point_vector)

            #parse northing / easting values
            if any(_ne) and not all(_ne):
                self.errors.append('(Easting, Northing) Incomplete: ( %s, %s)' % tuple(_ne))

            elif all(_ne):

                try:
                    point_vector.y = float(_ne[0])
                    point_vector.x = float(_ne[1])

                except:
                    self.errors.append('(Easting, Northing) Invalid: (%s, %s)' % tuple(_ne))

                geo_vector.x, geo_vector.y = Utils.coordinates_to_distance_bearing(_points[-1], point_vector)

            _points.append(point_vector)
            _geometry.append(geo_vector)

        self.Object.Points = _points
        self.Object.Geometry = _geometry

    def get_intersection_coordinates(self):
        '''
        Return the object intersection point with it's parent alignment
        '''

        int_eq = self.Object.Intersection_Equation
        sta_eqs = self.Object.Alignment_Equations

        if not self.Object.Parent_ID:
            return None

        if not self.Object.Intersection_Equation:
            return None

        objs = App.ActiveDocument.getObjectsByLabel(self.Object.Parent_ID + '_Horiz')

        if not objs:
            return None

        parent_coord = self._get_coordinate_at_station(int_eq[0], objs[0])

        start_sta = 0.0

        #if the first equation's Back is 0.0, the Forward is the starting station
        if sta_eqs[0][0] == 0.0:
            start_sta = sta_eqs[0][1]

        distance = int_eq[1] - start_sta

        child_coord = self.Object.Points[0]

        if distance > 0.0:

            child_coord = self.Object.Shape.discretize(Distance=distance)[1]

        return(parent_coord, child_coord)

    def set_data(self, data):
        '''
        Assign curve data to object, parsing and converting to coordinate form
        '''

        self.no_execute = True

        self.assign_meta_data(data['meta'])
        self.assign_station_data(data['station'])

        datum = App.Vector(0.0, 0.0, 0.0)

        self.assign_geometry_data(datum, data['data'])

        delattr(self, 'no_execute')

        if not self.Object.Parent_ID:
            return

        self.execute(self.Object)

        self.no_execute = True

        coordinates = self.get_intersection_coordinates()

        if not coordinates:
            return

        #subtract the child coordinate's intersection point from the parent's
        delta = coordinates[0].sub(coordinates[1])

        #add the delta to the placement base to get the new placement
        self.Object.Placement.Base = self.Object.Placement.Base.add(delta)

        delattr(self, 'no_execute')

    def _get_coordinate_at_station(self, station, parent):
        '''
        Return the distance along an alignment from the passed station as a float
        '''

        equations = parent.Alignment_Equations
        print(equations)

        #default starting station unles otherwise specified
        start_sta = 0.0
        start_index = 0

        #if the first equation's back value is zero, it's forward value is the starting station
        if equations[0][0] == 0.0:
            start_sta = equations[0][1]
            start_index = 1

        distance = 0

        if len(equations) > 1:

            #iterate the equation list, locating the passed station
            for _eqn in equations[start_index:]:

                #does station fall between previous forward and current back?
                if start_sta <= station <= _eqn[0]:
                    break

                #otherwise, accumulate the total distance between the previous forward and current back
                distance += _eqn[0] - start_sta

                #set the starting station to the current forward
                start_sta = _eqn[1]

        distance += station - start_sta

        #station bound checks
        if distance > parent.Shape.Length:
            return None

        if distance < 0.0:
            return None

        #discretize valid distance
        result = parent.Shape.discretize(Distance=distance)[1]

        if len(result) < 2:
            print('failed to discretize')
            return None

        return result

    def _discretize_geometry(self, segments):
        '''
        Discretizes the alignment geometry to a series of vector points
        '''

        segments = 2
        geometry = self.Object.Geometry[1:]
        prev_geo = self.Object.Geometry[0]
        prev_coord = App.Vector(0.0, 0.0, 0.0)
        prev_curve_tangent = 0.0

        coords = [App.Vector(0.0, 0.0, 0.0)]

        for _geo in geometry:

            distance = prev_geo[0]
            bearing_in = math.radians(prev_geo[1])
            bearing_out = math.radians(_geo[1])
            radius = prev_geo[2]
            central_angle = bearing_out - bearing_in
            curve_dir = central_angle / abs(central_angle)
            central_angle = abs(central_angle)

            print('distance: ', distance)
            print('bearing_in', bearing_in)
            print('baering_out', bearing_out)
            print('radius', radius)
            print('central_nagle', central_angle)
            print('curve_dir', curve_dir)

            if central_angle >= math.pi:
                central_angle = (math.pi * 2.0) - central_angle

            curve_tangent = radius * math.tan(central_angle / 2.0)

            print('curve_tangent', curve_tangent)
            print('prev_curve_tangent', prev_curve_tangent)

            prev_tan_len = distance - curve_tangent - prev_curve_tangent

            if prev_tan_len < DocumentProperties.MinimumTangentLength.get_value():
                continue

            seg_len = prev_tan_len / float(segments)

            print('prev_tan_len', prev_tan_len)
            prev_curve_tangent = curve_tangent

            _forward = App.Vector(math.sin(bearing_in), math.cos(bearing_in), 0.0)

            #discretize the tangent
            for _i in numpy.arange(seg_len, prev_tan_len + seg_len / 2.0, seg_len):
                _x = App.Vector(_forward)
                coords.append(prev_coord.add(_x.multiply(_i)))

            #add the end of the tangent / start of the curve (PC)
            #coords.append(_forward.multiply(prev_tan_len))

            #zero radius means no curve.  We're done
            if radius == 0.0:
                continue

            _left = App.Vector(-_forward.y, _forward.x, 0.0)
            seg_rad = central_angle / float(segments)

            prev_coord = coords[-1]

            for _i in range(0, segments):

                _dfw = App.Vector(_forward)
                _dlt = App.Vector(-_left)

                delta = float(_i + 1) * seg_rad

                print('DELTA = ', delta)

                _dfw.multiply(radius * math.sin(delta))
                _dlt.multiply(curve_dir * radius * (1 - math.cos(delta)))

                print('dFW = ', _dfw)
                print('dLT = ', _dlt)
                coords.append(prev_coord.add(_dfw).add(_dlt))

            prev_geo = _geo
            prev_coord = coords[-1]

        print(coords)
        return coords

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

        #if curve.Bearing != 0.0:
            #azimuth = self._get_azimuth(math.radians(curve.Bearing), curve.Quadrant)

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

    def onChanged(self, obj, prop):

        print('propchange: ', prop)
        #dodge onChanged calls during initialization
        if hasattr(self, 'no_execute'):
            return

        print('changing prop: ', prop)
        if prop == "Segments":
            print('segments....')
            self.execute(obj)
            

    def execute(self, obj):
        '''
        Class execute for recompute calls
        '''

        if hasattr(self, 'no_execute'):
            return

        print('executing...')

        #res = Draft._BSpline(obj)
        res = Draft._Wire(obj)
        
        obj.Points = self._discretize_geometry(obj.Subdivisions)

        obj.Closed = False

        res.execute(obj)

_ViewProviderHorizontalAlignment = Draft._ViewProviderWire
