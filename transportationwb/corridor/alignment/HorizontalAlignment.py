
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
import Part
from transportationwb.ScriptedObjectSupport import Properties

_CLASS_NAME = 'Alignment'
_TYPE = 'Part::FeaturePython'

__title__ = _CLASS_NAME + '.py'
__author__ = "AUTHOR_NAME"
__url__ = "https://www.freecadweb.org"

def create(data, units='English', object_name='', parent=None):
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

    result = _Alignment(_obj)

    result.set_data(data)

    if not units == 'English':
        result.set_units(units)

    _ViewProviderAlignment(_obj.ViewObject)

    return result

class Headers():

    meta = ['ID', 'Parent_ID', 'Back', 'Forward']
    data = ['Northing', 'Easting', 'Bearing', 'Distance', 'Radius', 'Degree']
    complete = meta.extend(data)

class _Alignment():

    @staticmethod
    def doc_to_radius(value):
        '''
        Converts degree of curve value to radius
        '''

        _const_val = (180.0 * 100.0) / math.pi

        if self.Object.Units == 'English':
            _const_val = (180.0 * 304.80) / math.pi

        return _const_val / value

    def __init__(self, obj):
        '''
        Main class intialization
        '''

        self.Type = "_" + _CLASS_NAME
        self.Object = obj
        self.errors = []

        obj.Proxy = self

        #add class properties
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'String', 'Parent ID', 'ID of alignment parent', '')
        Properties.add(obj, 'Vector', 'Intersection Equation', 'Station equation for intersection with parent', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Alignment Equations', 'Station equation along the alignment', [])
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Geometry', 'Geometry defining the alignment', [])
        Properties.add(obj, 'String', 'Units', 'Alignment units', 'English', is_read_only=True)

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

        #data is stored in a list of dictionaries
        for item in data:

            if item['ID']:
                obj.ID = item['ID']

            if item['Parent ID']:
                obj.Parent_ID = item['Parent ID']

            #alignment and intersection station equations
            if item['Back'] and item['Forward']:

                _bk = 0.0
                _fwd = 0.0

                try:
                    _bk = float(item['Back'])
                    _fwd = float(item['Forward'])

                    _eqn = App.Vector(_bk, _fwd, 0.0)

                    if item['Parent ID']:
                        obj.Intersection_Equation = _eqn
                    else:
                        obj.Alignment_Equations.append(_eqn)

                except:
                    _err1 = 'Invalid station equation for object ' + item['ID'] + ':\n'
                    _err2 = 'Values: %s (back); %s (forward)' % (item['Back'], item['Forward'])
                    self.errors.append(_err1 + _err2)

            #alignment datum/starting station
            elif not item['Back'] and item['Forward']:

                _fwd = 0.0

                try:
                    _fwd = float(item['Forward'])
                    obj.Alignment.Equations.append(App.Vector(-1.0, _fwd, 0.0))
                except:
                    self.errors.append('Invalid datum station for object ' + item['ID'] + ': %s' %item['Forward'])

    def assign_geometry_data(self, data):
        '''
        Iterate the dataset, extracting geometric data
        Validate data
        Create separate items for each curve / tangent
        Assign Northing / Easting datums
        '''
        for item in data:

            _ne = [item['Northing'], item['Easting']]
            _db = [item['Distance'], item['Bearing']]
            _rd = [item['Radius'], item['Degree']]

            #parse degree of curve / radius values
            if _rd[0]:
                try:
                    _rd[0] = float(_rd[0])
                except:
                    self.errors.append('Invalid radius: %s' % _rd[0])

            elif _rd[1]:
                try:
                    _rd[1] = self.doc_to_radius(float(_rd[1]))
                except:
                    self.errors.append('Invalid degree of curve: %s' % _rd[1])

            #parse bearing / distance values
            if any(_db) and not all(_db):
                self.errors.append('(Distance, Bearing) Incomplete: (%s, %s)' % tuple(_db))
            
            elif all(_db):
                #get the last point in the geometry for the datum, unless empty
                datum = self.Object.Datum

                if self.Object.Geometry:
                    datum = self.Object.Geometry[-1]

                
            #parse northing / easting values
            if any(_ne) and not all(_ne):
                self.errors.append('(Easting, Northing) Incomplete: ( %s, %s)' % tuple(_ne))

            elif all(_ne):
                self.Object.Geometry.append(App.Vector(_ne[1], _ne[0]))

    def set_data(self, data):
        '''
        Curve data as a list of tuple('label', 'data')
        '''

        self.assign_meta_data(data)
        self.get_geometry_data(data)

        #split the dataset into metadata and curve data
        #parse the metadata, looking for errors
        #assign the metadata values to the object properties
        #parse the curve data, looking for errors
        #parse the curve data, converting parameters to Northing/Easting/Radius format

    def execute(self, obj):
        '''
        Class execute for recompute calls
        '''
        pass

class _ViewProviderAlignment(object):

    def __init__(self, vobj):
        '''
        View Provider initialization
        '''
        self.Object = vobj.Object

    def getIcon(self):
        '''
        Object icon
        '''
        return ''

    def attach(self, vobj):
        '''
        View Provider Scene subgraph
        '''
        pass

    def __getstate__(self):
        '''
        State method for serialization
        '''
        return None

    def __setstate__(self,state):

        '''
        State method for serialization
        '''
        return None
