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
from transportationwb.Geometry import Arc
from transportationwb.XML import XmlFpo

_CLASS_NAME = 'HorizontalAlignment'
_TYPE = 'Part::Part2DObjectPython'

__title__ = _CLASS_NAME + '.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"


def create(geometry, object_name='', units='English', parent=None):
    '''
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    parent - Optional.  Reference to existing DocumentObjectGroup.  Defaults to ActiveDocument
    data - a list of the curve data in tuple('label', 'value') format
    '''

    if not geometry:
        print('No curve geometry supplied')
        return

    _obj = None
    _name = _CLASS_NAME

    if object_name:
        _name = object_name

    if parent:
        _obj = parent.newObject(_TYPE, _name)
    else:
        _obj = App.ActiveDocument.addObject(_TYPE, _name)

    result = _HorizontalAlignment(_obj, _name)
    result.set_geometry(geometry)

    Draft._ViewProviderWire(_obj.ViewObject)

    App.ActiveDocument.recompute()
    return result

#Construction order:
#Calc arc parameters
#Sort arcs
#calculate arc start coordinates by internal position and apply to arcs

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
        self.xml_fpo = None
        self.geometry = []

        obj.Label = label
        obj.Closed = False

        if not label:
            obj.Label = obj.Name

        #add class properties
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'Vector', 'Intersection Equation', 
                      'Equation for intersection with parent alignment', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Station Equations', 
                      'Station equation along the alignment', [])
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting',
                       App.Vector(0.0, 0.0, 0.0))

        Properties.add(obj, 'String', 'Units', 'Alignment units', 'English', is_read_only=True)
        Properties.add(obj, 'VectorList', 'PIs',
                       'Discretization of Points of Intersection (PIs) as a list of vectors', [])
        Properties.add(obj, 'Link', 'Parent Alignment', 'Links to parent alignment object', None)

        subdivision_desc = 'Method of Curve Subdivision\n\nTolerance - ensure error between segments and curve is approximately (n)\nInterval - Subdivide curve into segments of a fixed length (n)\nSegment - Subdivide curve into (n) equal-length segments'

        obj.addProperty('App::PropertyEnumeration', 'Method', 'Segment', subdivision_desc
                       ).Method = ['Tolerance', 'Interval','Segment']

        Properties.add(obj, 'Float', 'Segment.Seg_Value',
                      'Set the curve segments to control accuracy', 1.0)

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

    def set_geometry(self, geometry):
        '''
        Assign geometry to the alignment object
        '''

        for arc in geometry['geometry']:
            print('-----------\n', arc)

            if arc['Type'] == 'arc':
                result = Arc.get_arc_parameters(arc)

                if arc:
                    self.geometry.append(result)

        self.geometry = self.sort_geometry(self.geometry)

    @staticmethod
    def _find_adjacent(index, data):
        '''
        Return the first match of adjacent curves
        '''

        print('---adjacent---', data)

        curve = data[index]
        end_point = curve['End']

        if not end_point:
            return None

        for _i in range(0, len(data)):

            if _i == index:
                continue

            start_point = data[_i].get('Start')

            if not start_point:
                continue

            #Points must be within a millimeter to be coincident
            if end_point.distanceToPoint(start_point) < 1.0:
                return _i

        return None

    def _find_nearest(self, index, data):
        '''
        Return the nearest geometry with the same bearing
        '''
        curve = data[index]
        out_bearing = curve.get('OutBearing')

        if not out_bearing:
            return None

        lst = []

        #matching bearings may be adjacent curves
        for _i, _v in enumerate(data):

            if out_bearing == _v.get('InBearing'):
                lst.append(_i)

        #no matches found
        if not lst:
            return None

        #one match found 
        if len(lst) == 1:
            return lst[0]

        #Multiple matches found.
        #Pick the nearest adjacent curve
        max_dist = None
        nearest_pi = None
        pi_1 = curve.get('PI')

        if not pi_1:
            self.errors.append('Missing PI in ' + self.Object.ID)
            return None

        for _i in lst:

            if _i == index:
                continue

            pi_2 = data[_i].get('PI')

            if not pi_2:
                self.errors.append('Missing PI in ' + self.Object.ID)
                return None

            dist = pi_1.distanceToPoint(pi_2)

            if not dist:
                continue

            if max_dist is None:
                max_dist = dist

            elif dist < max_dist:
                max_dist = dist
                nearest_pi = _i

        return nearest_pi

    def sort_geometry(self, data):
        '''
        Validate the coordinate geometry data by ensuring
        PI data is continuous within the alignment and ordering the
        internal data set accordingly.
        data - a list of curve dictionaries
        '''

        matches = []

        print(data)
        data_len = len(data)

        for _i in range(0, data_len):
            
            ################# Test for coincident endpoints
            _j = self._find_adjacent(_i, data)

            if not _j is None:
                matches.append([_i, _j])

            ############## Test for identical bearings
            _j = self._find_nearest(_i, data)

            if not _j is None:
                matches.append([_i, _j])

        #the number of matches (pairs) should be
        #one less than the number of curves
        if len(matches) != data_len - 1:
            self.errors.append('%d curves found, %d unmatched'
                               % (data_len, data_len - len(matches) - 1))
            self.errors.append('Alignment ' + self.Object.ID + ' is discontinuous.')
            return None

        ############## Order the list of matches
        ordered_list = matches
        old_len = len(ordered_list) + 1

        while len(ordered_list) < old_len:
            old_len = len(ordered_list)
            ordered_list = self._order_list(ordered_list)

        geo = data

        ############### Rebuild the data set in the correct order
        if ordered_list[0] != list(range(0, data_len)):
            geo = [data[_i] for _i in ordered_list[0]]

        return geo

    @staticmethod
    def _order_list(tuples):
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

    def _get_internal_station(self, station):
        '''
        Using the station equations, determine the internal station
        (position) along the alingment
        '''

        start_sta = self.Object.Station_Equations[0].y
        eqs = self.Object.Station_Equations

        #default to distance from starting station
        position = 0.0

        for _eq in eqs[1:]:

            #add the deistance and quit if the station falls within the equation
            if start_sta < station < _eq.x:
                position += station - start_sta
                break

            #increment the position by the equaion length and
            #set the starting station to the next equation
            position += _eq.x - start_sta
            start_sta = _eq.y

        #no more equations - station falls outside of last equation
        return position

    def _get_coordinate_at_station(self, station, parent):
        '''
        Return the coordinate position of a station along the alignment
        '''

        ###Need to:
        # 1.  Determine the internal station
        # 2.  Get the geometry starting at the nearest internal station
        #   a.  Option #1
        #       i. Iterate geometry, accumulating lengths
        #       ii. Stop when accumulation > internal station
        #   b.  Option #2
        #       i. Pre-calculate internal station with start of geometry
        #       ii. Iterate geometry, looking for nearest lesser internal station
        # 3.  Calculate the coordinate along the geometry for the remainder of the distance

        #Option #2 above requires:
        #   Known datum passed with geometry

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

    def discretize_geometry(self):
        '''
        Discretizes the alignment geometry to a series of vector points
        '''

        interval = self.Object.Seg_Value
        interval_type = self.Object.Method
        geometry = self.geometry
        points = []

        #discretize each arc in the geometry list,
        #store each point set as a sublist in the main points list
        for curve in geometry:

            if curve['Type'] == 'arc':

                curve_points = [curve[_key] for _key in ['Start', 'End', 'Center']]

                if all(curve_points):

                    curve_params = Arc.calc_arc_parameters(curve_points)

                    for key, value in curve_params.items():
                        curve[key] = value

                points.append(Arc.get_points(curve, interval, interval_type))

            if curve['Type'] == 'line':

                points.append([curve['Start'], curve['End']])

        #store the last point of the first geometry for the next iteration
        _prev = points[0][-1]
        result = points[0]

        #iterate the point sets, adding them to the result set
        #and eliminating any duplicate points
        for item in points[1:]:

            if _prev.sub(item[0]).Length < 0.0001:
                result.extend(item[1:])
            else:
                result.extend(item)

            _prev = item[-1]

        return result

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

        self.Object.Points = self.discretize_geometry()

        super(_HorizontalAlignment, self).execute(obj)
        #self.Object.Placement.Base = self.Object.Placement.Base.add(self.get_intersection_delta())
        #super(_HorizontalAlignment, self).execute(obj)

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