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
from transportationwb.Geometry import Arc, Support
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
        self.meta = {}

        obj.Label = label
        obj.Closed = False

        if not label:
            obj.Label = obj.Name

        #add class properties

        #metadata
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'String', 'oID', 'Object ID', '')
        Properties.add(obj, 'Length', 'Length', 'Alignment length', 0.0, is_read_only = True)
        Properties.add(obj, 'String', 'Description', 'Alignment description', '')

        obj.addProperty(
            'App::PropertyEnumeration', 'Status', 'Base', 'Alignment status'
            ).Status = ['existing', 'proposed', 'abandoned', 'destroyed']

        #Properties.add(obj, 'String', 'Units', 'Alignment units', 'English', is_read_only=True)

        #station
        #Properties.add(obj, 'Vector', 'Intersection Equation', 
        #              'Equation for intersection with parent alignment', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Station Equations',
                       'Station equation along the alignment', [])
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting',
                       App.Vector(0.0, 0.0, 0.0))

        #geometry
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

        self.assign_meta_data(geometry)
        self.assign_station_data(geometry)

        _geo_list = geometry['geometry']

        for _i in range(0, len(_geo_list)):

            _geo = _geo_list[_i]

            if _geo['Type'] == 'arc':

                result = Arc.get_arc_parameters(arc)

                if result:
                    _geo_list[_i] = result
                else:
                    self.errors.append('Undefined arc')
                    continue

            elif _geo['Type'] == 'line':

                continue

        geometry = self.validate_stationing(geometry)

        if not geometry:
            return None

        geometry = self.validate_bearings(geometry)

        if not geometry:
            return None

        geometry = self.validate_coordinates(geometry)

        if not geometry:
            return None

        self.geometry = geometry

    def validate_coordinates(self, geometry):
        '''
        Iterate the geometry, testing for incomplete / incorrect station / coordinate values
        Fix them where possible, error if values cannot be resolved
        '''

        #calculate distance bewteen curve start and end using
        #internal station and coordinate vectors

        _truth = []
        _prev_geo = geometry[0]



        for _geo in geometry[1:]:
            print('\n\n--- Previous Geo ---', _prev_geo)
            print('\n--- geo ----', _geo)
            _vector = _geo['End'].sub(_prev_geo['Start'])
            _sta_len = abs(_geo['InternalStation'][0] - _prev_geo['InternalStation'][1])

            _delta = (_vector.Length - _sta_len) / Units.scale_factor()
            print('\n--- delta: ---', delta)

            if not Support.within_tolerance(delta):
                bearing_angle = Support.get_bearing(_vector)

                if Support.within_tolerance(bearing_angle, _geo['BearingIn']):
                    _geo['StartStation'] = 
            _truth.append(Support.within_tolerance((_vector_len - _sta_len) / Units.scale_factor()))

            _prev_geo = _geo

        if all(_truth):
            return geometry


        _truth_shift = [False] + _truth[:len(_truth)]

        print('--- truth ---', _truth)
        print('--- truth-shift ---', _truth_shift)
        #xor of lists tells us which curves are now correctible
        result = [_x ^ _y for _x, _y in zip(_truth, _truth_shift)]

        print('--- truth XOR: ---', result)
        return geometry

    def validate_bearings(self, geometry):
        '''
        Validate the bearings between geometry, ensuring they are equal
        '''

        if len(geometry) < 2:
            return geometry

        prev_bearing = geometry[0]['BearingOut']

        for _geo in geometry[1:]:

            _b = _geo.get('BearingIn')

            if _b is None:
                self.errors.append('Invalid bearings ({0:.4f}, {1:.4f}) at curve {2}'
                                   .format(prev_bearing, _b, _geo)
                                  )
                return None

            if not Support.within_tolerance(_b, prev_bearing):
                self.errors.append('Bearing mismatch ({0:.4f}, {1:.4f}) at curve {2}'
                                   .format(prev_bearing, _b, _geo)
                                  )

                return None

            prev_bearing = _geo.get('BearingOut')

        return geometry

    def validate_stationing(self, geometry):
        '''
        Iterate the geometry, calculating the internal start station based on the actual station
        and storing it in an 'InternalStation' parameter tuple for the start and end of the curve
        '''

        for _geo in geometry:

            _geo['InternalStation'] = None
            start_station = _geo.get('StartStation')

            if start_station is None:
                continue

            int_sta = self._get_internal_station(start_station)
            _geo['InternalStation'] = (int_sta, int_sta + _geo['Length'])

        return geometry

    def _get_internal_station(self, station):
        '''
        Using the station equations, determine the internal station
        (position) along the alingment, scaled to the document units
        '''
        start_sta = self.Object.Station_Equations[0].y
        eqs = self.Object.Station_Equations

        #default to distance from starting station
        position = 0.0

        for _eq in eqs[1:]:

            #if station falls within equation, quit
            if start_sta < station < _eq.x:
                break

            #increment the position by the equaion length and
            #set the starting station to the next equation
            position += _eq.x - start_sta
            start_sta = _eq.y

        #add final distance to position
        position += station - start_sta

        return position * Units.scale_factor()

    def _get_station_coordinate(self, geometry, station):
        '''
        Return the coordinate position of a station along the alignment
        '''

        target_sta = self._get_internal_station(station)

        if target_sta < 0.0:
            return None

        cur_sta = 0.0
        result = App.Vector()

        #find the coordinates
        for _geo in  geometry:

            if cur_sta + _geo.Length > target_sta:

                if _geo['Type'] == 'arc':
                    result = Arc.get_coordinate(_geo, target_sta - cur_sta)

                elif _geo['Type'] == 'line':
                    result = Line.get_coordiante(_geo, target_sta - cur_sta)

                break

            cur_sta += _geo.Length

        return result

    def assign_meta_data(self, geometry):
        '''
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        '''

        obj = self.Object

        meta = geometry['meta']

        if meta.get('ID'):
            obj.ID = meta['ID']

        if meta.get('Description'):
            obj.Description = meta['Description']

        if meta.get('ObjectID'):
            obj.ObjectID = meta['ObjectID']

        if meta.get('Length'):
            obj.Length = meta['Length']

        if meta.get('Status'):
            obj.Status = meta['Status']

    def assign_station_data(self, geometry):
        '''
        Assign the station and intersection equation data
        '''

        obj = self.Object

        _eqs = geometry['station']

        _eqn_list = []
        _start_sta = Utils.to_float(geometry['meta'].get('StartStation'))

        if _start_sta:
            _eqn_list.append(App.Vector(0.0, _start_sta, 0.0))
        else:
            self.errors.append('Unable to convert starting station %s'
                               % geometry['meta'].get('StartStation')
                              )

        for _eqn in _eqs:

            eq_vec = None

            #default to increasing station if unspecified
            if not _eqn['Direction']:
                _eqn['Direction'] = 1.0

            try:
                eq_vec = App.Vector(
                    float(_eqn['Back']), float(_eqn['Ahead']), float(_eqn['Direction'])
                    )

            except:
                self.errors.append('Unable to convert station equation (%s)'
                                   % (_eqn)
                                  )
                continue

            _eqn_list.append(eq_vec)

        obj.Station_Equations = _eqn_list

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