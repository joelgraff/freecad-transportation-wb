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
Class for managing 2D Horizontal Alignments
'''
import math
import os
from shutil import copyfile

import FreeCAD as App
import FreeCADGui as Gui
import Draft
import numpy

from xml.etree import ElementTree as etree

from transportationwb.ScriptedObjectSupport import Properties, Units, Utils, DocumentProperties, Singleton
from transportationwb.Project.AlignmentXmlImporter import AlignmentXmlImporter
from transportationwb.Project.AlignmentXmlExporter import AlignmentXmlExporter

_CLASS_NAME = 'HorizontalAlignment'
_TYPE = 'Part::Part2DObjectPython'

__title__ = _CLASS_NAME + '.py'
__author__ = "AUTHOR_NAME"
__url__ = "https://www.freecadweb.org"

meta_fields = ['ID', 'StartStation', 'Description', 'Status', 'Length', 'Units']
data_fields = ['Direction', 'Length', 'InBearing', 'OutBearing', 'Radius', 'PI', 'PcStation']
station_fields = ['Back', 'Ahead', 'Position', 'Direction', 'Description']

class _XmlFile(metaclass=Singleton.Singleton):
    '''
    Const / class that manage
    '''

    @staticmethod
    def instance():
        '''
        Return the singleton instance of the class
        '''

        return Singleton.Singleton.instance_of(_XmlFile)

    def __init__(self, data):
        '''
        Initialize the XML file singleton
        Data consists of a dictionary of alignment objects
        '''

        self.template_path = 'data/landXML-imperial-template.xml'

        if Units.is_metric_doc():
            self.template_path = 'data/landXML-metric-template.xml'

        self.target_path = App.ActiveDocument.TransientDir + '/alignments.xml'

        self.data = data

    def update(self, key, value):
        '''
        Update the dictionary
        '''

        self.data[key] = value

    def write(self):
        '''
        Write the dictionary to file
        '''

        tree = etree.parse(self.template_path)
        AlignmentXmlExporter.write(tree, self.data, self.target_path)

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

    #if not units == 'English':
        #result.set_units(units)

    Draft._ViewProviderWire(_obj.ViewObject)

    App.ActiveDocument.recompute()
    return result

class _HorizontalAlignment(Draft._Wire):

    def __init__(self, obj, label=''):
        '''
        Default Constructor
        '''

        super(_HorizontalAlignment, self).__init__(obj)

        self.no_execute = True

        obj.Proxy = self
        self.Type = _CLASS_NAME
        self.Object = obj
        self.errors = []
        self.geometry = None

        obj.Label = label
        obj.Closed = False

        if not label:
            obj.Label = obj.Name

        #add class properties
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'Vector', 'Intersection Equation', 'Equation for intersection with parent alignment', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Station Equations', 'Station equation along the alignment', [])
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting', App.Vector(0.0, 0.0, 0.0))
        #Properties.add(obj, 'StringList', 'Geometry', 'Geometry defining the alignment', [])
        #THIS SHOULD BE MANAGED UNDER CUSTOM ALIGNMENTS GROUP OBJECT
        #Properties.add(obj, 'FileIncluded','Alignment XML File', 'Filepath for alignment XML', )

        Properties.add(obj, 'String', 'Units', 'Alignment units', 'English', is_read_only=True)
        Properties.add(obj, 'VectorList', 'PIs', 'Discretization of Points of Intersection (PIs) as a list of vectors', [])
        Properties.add(obj, 'Link', 'Parent Alignment', 'Links to parent alignment object', None)

        subdivision_desc = 'Method of Curve Subdivision\n\nTolerance - ensure error between segments and curve is approximately (n)\nInterval - Subdivide curve into segments of a fixed length (n)\nSegment - Subdivide curve into (n) equal-length segments'

        obj.addProperty('App::PropertyEnumeration', 'Method', 'Segment', subdivision_desc).Method = ['Tolerance', 'Interval','Segment']

        Properties.add(obj, 'Float', 'Segment.Seg_Value', 'Set the curve segments to control accuracy', 1.0)

        delattr(self, 'no_execute')

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onDocumentRestored(self, fp):
        '''
        Restore object references on reload
        '''

        self.Object = fp

        #HANDLE AT GROUP LEVEL?
        self.geometry = AlignmentXmlImporter.import_model(App.ActiveDocument.TransientDir + '/alignments.xml', 'r')

    def set_units(self, units):
        '''
        Sets the units of the alignment
        Does not recompute values
        '''

        self.Object.Units = units

    def assign_meta_data(self, data):
        '''
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        '''

        obj = self.Object

        if data['ID']:
            obj.ID = data['ID']

    def assign_station_data(self, data):
        '''
        Assign the station equation data
        '''

        obj = self.Object

        for key in data.keys():

            back = key[0]
            ahead = key[1]

            eqns = obj.Station_Equations
            eqns.append(App.Vector(back, ahead, 0.0))

            obj.Station_Equations = eqns

    def assign_geometry_data(self, data):
        '''
        Validate the coordinate geometry data by ensuring
        PI data is continuous within the alignment and ordering the
        internal data set accordingly.
        data - a list of curve dictionaries
        '''

        #XML_CURVE_KEYS = {'rot':'Direction', 'dirStart': 'InBearing', 'dirEnd': 'OutBearing', 'staStart': 'PcStation', 'radius': 'Radius'}
        #XML_LINE_KEYS = {'dir': 'Direction', 'length': 'Length', 'staStart': 'PcStation'}

        matches = []

        data_len = len(data)

        for _i in range(0, data_len):
            
            ################# Test for coincident endpoints
            curve_1 = data[_i]
            end_point = curve_1.get('End')

            if end_point:

                #test for coincident start / end points
                for _j in range(0, data_len):

                    start_point = data[_j].get('Start')

                    if start_point:

                        #arbitrary tolerance check to determine if points are close enough to be merged
                        if end_point.distanceToPoint(start_point) < 1.0:
                            matches.append([_i, _j])
                            break

                #skip the rest if a match was found
                if matches[-1][0] == _i:
                    continue

            ############## Test for identical bearings
            out_bearing = curve_1.get('OutBearing')

            if out_bearing:

                lst = []

                for _j in range(0, data_len):

                    #matching bearings may be adjacent curves
                    if out_bearing == data[_j].get('InBearing'):
                        lst.append(_j)

                #no matches found, skip the remainder of the iteration
                if not lst:
                    continue

                #one match found, save it and move on
                if len(lst) == 1:
                    matches.append([_i, lst[0]])
                    continue

                #still here?  Multiple matches found.
                #test for more than one curve with a matching bearing,
                #picking the shortest as the adjacent curve
                match = lst[0]
                max_dist = None
                nearest_pi = None

                for _x in lst:

                    pi_1 = curve_1.get('PI')
                    pi_2 = data[_j].get('PI')

                    if not pi_1 or not pi_2:
                        print ('Missing PI in ' + self.Object.ID)
                        return None

                    if pi_1 != pi_2:

                        dist = pi_1.distanceToPoint(pi_2)

                        if max_dist:
                            if dist < max_dist:
                                max_dist = dist
                                nearest_pi = _j

                if nearest_pi:
                    matches.append([_i, nearest_pi])

        if len(matches) != data_len - 1:
            print('%d curves found, %d unmatched' % (data_len, data_len - len(matches) - 1))
            print('Alignment ', self.Object.ID, ' is discontinuous.')
            return None

        ordered_list = matches
        old_len = len(ordered_list) + 1

        while len(ordered_list) < old_len:
            old_len = len(ordered_list)
            ordered_list = self._order_list(ordered_list)

        self.Object.Geometry = data

        #with an ordered list of indices, create a new data set in the correct order
        if ordered_list[0] != list(range(0,data_len)):
            self.Object.Geometry = [data[_i] for _i in ordered_list[0]]

    def _order_list(self, tuples):
        '''
        Combine a list of tuples where endpoints of two tuples match
        '''

        if len(tuples) == 1:
            return tuples

        tuple_end = len(tuples[0]) - 1
        tuple_count = len(tuples)
        tuple_pairs = []

        for _i in range(0, tuple_count):

            _tpl1 = tuples[_i]

            for _tpl2 in tuples[(_i + 1):]:

                ordered_tuple = None

                if _tpl1[0] == _tpl2[tuple_end]:
                    ordered_tuple = _tpl2
                    ordered_tuple.extend(_tpl1[1:])

                elif _tpl1[tuple_end] == _tpl2[0]:
                    ordered_tuple = _tpl1 
                    ordered_tuple.extend(_tpl2[1:])

                if ordered_tuple:
                    tuple_pairs.append(ordered_tuple)

        return tuple_pairs

    def set_data(self, data):
        '''
        Assign curve data to object, parsing and converting to coordinate form
        '''

        self.no_execute = True

        self.assign_meta_data(data['meta'])
        self.assign_station_data(data['station'])

        #int_eq = self.Object.Intersection_Equation

        #if int_eq.Length:
        #    datum = self._get_coordinate_at_station(int_eq[0], self.Object.Parent_Alignment) / 304.80

        self.assign_geometry_data(data['curve'])

        delattr(self, 'no_execute')

        self.Object.Points = self._discretize_geometry()

    def _get_coordinate_at_station(self, station, parent):
        '''
        Return the distance along an alignment from the passed station as a float
        '''

        equations = parent.Alignment_Equations

        #default starting station unles otherwise specified
        start_sta = 0.0
        start_index = 0

        #if the first equation's back value is zero, it's forward value is the starting station
        if equations:
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
        if distance > parent.Shape.Length or distance < 0.0:
            print('Station distance exceeds parent limits (%f not in [%f, %f]' % (station, start_sta, start_sta + parent.Shape.Length))
            return None

        #discretize valid distance
        result = parent.Shape.discretize(Distance=distance * 304.80)[1]

        if len(result) < 2:
            print('failed to discretize')
            return None

        return result

    @staticmethod
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

    @staticmethod
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

        seg_rad = _HorizontalAlignment.calc_angle_increment(angle, radius, interval, interval_type)

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

    @staticmethod
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
        arc_coords.extend(_HorizontalAlignment.discretize_arc(arc_start, bearing + (theta_spiral * curve_dir), radius, curve_dir * (angle - (2 * theta_spiral)), interval, interval_type))

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

    def _discretize_geometry(self):
        '''
        Discretizes the alignment geometry to a series of vector points
        '''

        interval = self.Object.Seg_Value
        interval_type = self.Object.Method

        #alignment construction requires a 'look ahead' at the next element
        #This implementation does a 'look back' at the previous.
        #Thus, iteration starts at the second element and
        #the last element is duplicated to ensure it is constructed.
        geometry = self.Object.Geometry

        if not geometry:
            print('No geometry defined.  Unnable to discretize')
            return None

        prev_geo = [float(_i) for _i in geometry[0].split(',')]

        #test in case we only have one geometric element
        if len(geometry) > 1:
            geometry = geometry[1:]
            geometry.append(geometry[-1])

        prev_curve_tangent = 0.0

        coords = [App.Vector(0.0, 0.0, 0.0)]

        for geo_string in geometry:

            #convert the commo-delimited string of floats into a list of strings, then to floats
            _geo = [float(_i) for _i in geo_string.split(',')]

            bearing_in = math.radians(prev_geo[1])
            bearing_out = math.radians(_geo[1])

            curve_dir, central_angle = Utils.directed_angle(Utils.vector_from_angle(bearing_in), Utils.vector_from_angle(bearing_out))

            curve_tangent = prev_geo[2] * math.tan(central_angle / 2.0)

            #alternate calculation for spiral curves
            if prev_geo[3] > 0.0:
                curve_tangent = (prev_geo[3] / 2.0) + (prev_geo[2] + ((prev_geo[3]**2)/(24 * prev_geo[2]))) * math.tan(central_angle / 2.0)

            #previous tangent length = distance between PI's minus the two curve tangents
            prev_tan_len = prev_geo[0] - curve_tangent - prev_curve_tangent

            #skip if our tangent length is too short leadng up to a curve (likely a compound curve)
            if prev_tan_len >= 1:
                coords.extend(self.discretize_arc(coords[-1], bearing_in, prev_tan_len, 0.0, 0.0, 'Segment'))

            #zero radius means no curve.  We're done
            if prev_geo[2] > 0.0:
                if prev_geo[3] > 0.0:
                    coords.extend(self.discretize_spiral(coords[-1], bearing_in, prev_geo[2], central_angle * curve_dir, prev_geo[3], interval, interval_type))
                else:
                    coords.extend(self.discretize_arc(coords[-1], bearing_in, prev_geo[2], central_angle * curve_dir, interval, interval_type))

            prev_geo = _geo
            prev_curve_tangent = curve_tangent

        return coords

    def onChanged(self, obj, prop):

        #dodge onChanged calls during initialization
        if hasattr(self, 'no_execute'):
            return

        if prop == "Method":

            _prop = obj.getPropertyByName(prop)

            if _prop == 'Interval':
                self.Object.Seg_Value = 100.0

            elif _prop == 'Segment':
                self.Object.Seg_Value = 10.0

            elif _prop == 'Tolerance':
                self.Object.Seg_Value = 1.0

    def execute(self, obj):

        if hasattr(self, 'no_execute'):
            return

        print('executing ', self.Object.Label)

        self.Object.Points = self._discretize_geometry()

        super(_HorizontalAlignment, self).execute(obj)
        self.Object.Placement.Base = self.Object.Placement.Base.add(self.get_intersection_delta())
        super(_HorizontalAlignment, self).execute(obj)

class _ViewProviderHorizontalAlignment:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None
    
    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        pass
    
    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        pass