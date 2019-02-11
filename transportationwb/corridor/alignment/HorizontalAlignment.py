
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

from transportationwb.ScriptedObjectSupport import Properties, Units, Utils

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

                    print ('processing eqwn: ', _eqn)
                    back = -1
                    forward = -1

                    try:
                        back = float(_eqn[0])
                        forwaad = float(_eqn[1])

                    except:
                        self.errors.append('Unable to convert station equation (Back: %s, Forward: %s)' % (_eqn[0], _eqn[1]))
                        continue

                    obj.Alignment_Equations.append(App.Vector(back, forward, 0.0))

            else:

                back = -1
                forward = -1

                try:
                    back = _eqn[0]
                    forward = _eqn[1]

                except:
                    self.errors.append('Unable to convert intersection equation with parent %s: (Back: %s, Forward: %s' % (key, _eqn[0], _eqn[1]))
                
                obj.Parent_ID = key
                obj.Intersection_Equation = App.Vector(data[key][0], data[key][1])

    def assign_geometry_data(self, datum, data):
        '''
        Iterate the dataset, extracting geometric data
        Validate data
        Create separate items for each curve / tangent
        Assign Northing / Easting datums
        '''

        _geometry = [datum]

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
                    _db[1] = math.radians(float(_db[1]))

                except:
                    self.errors.append('(Distance, Bearing) Invalid: (%s, %s)' % tuple(_db))

                #successful conversion of distance/bearing to floats

                #set values to geo_vector, adding the previous position to the new one
                geo_vector = Utils.distance_bearing_to_coordinates(_db[0], _db[1])
                geo_vector = _geometry[-1].add(geo_vector)

            #parse northing / easting values
            if any(_ne) and not all(_ne):
                self.errors.append('(Easting, Northing) Incomplete: ( %s, %s)' % tuple(_ne))

            elif all(_ne):

                try:
                    geo_vector.y = float(_ne[0])
                    geo_vector.x = float(_ne[1])

                except:
                    self.errors.append('(Easting, Northing) Invalid: (%s, %s)' % tuple(_ne))

            print('appending: ', geo_vector)

            _geometry.append(geo_vector)

        self.Object.Geometry = _geometry

    def get_parent_datum(self):
        '''
        Return the object datum as northing / easting, relative to
        it's intersection with it's parent, if assigned
        '''

        result = App.Vector(0.0, 0.0, 0.0)

        if not self.Object.Parent_ID:
            return result

        if self.Object.Intersection_Equation:
            return result

        objs = App.ActiveDocument.getObjectsByLabel(self.Object.Parent_ID + ' Horiz')

        if not objs:
            return result

        return objs[0].get_coordinate_at_station(self.Object.Intersection_Equation[0])

    def set_data(self, data):
        '''
        Assign curve data to object, parsing and converting to coordinate form
        '''

        self.no_execute = True

        self.assign_meta_data(data['meta'])
        self.assign_station_data(data['station'])
        datum = self.get_parent_datum()
        self.assign_geometry_data(datum, data['data'])

        delattr(self, 'no_execute')

    def execute(self, obj):
        '''
        Class execute for recompute calls
        '''

        if hasattr(self, 'no_execute'):
            return

        res = Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = obj.Geometry

        res.execute(obj)

_ViewProviderHorizontalAlignment = Draft._ViewProviderWire
