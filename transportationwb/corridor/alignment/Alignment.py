
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
import FreeCAD as App
import Part
from transportationwb.ScriptedObjectSupport import Properties

_CLASS_NAME = 'Alignment'
_TYPE = 'Part::FeaturePython'

__title__ = _CLASS_NAME + '.py'
__author__ = "AUTHOR_NAME"
__url__ = "https://www.freecadweb.org"

def create(data, object_name='', parent=None):
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

    _ViewProviderAlignment(_obj.ViewObject)

    
    return result

class _Alignment():

    def __init__(self, obj):
        '''
        Main class intialization
        '''

        self.Type = "_" + _CLASS_NAME
        self.Object = obj

        obj.Proxy = self

        #add class properties
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'String', 'Parent ID', 'ID of alignment parent', '')
        Properties.add(obj, 'Vector', 'Equation', 'Station equation for intersection with parent', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Data', 'Curve data defining the alignment', [])

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

    def set_id(self, text=''):
        '''
        Sets the ID of the alignment.
        If no text / empty string is provided, ID is assigned the object label
        '''

        if not text:
            text = self.Object.label

        self.Object.ID.Value = text

    def set_data(self, data):
        '''
        Curve data as a list of tuple('label', 'data')
        '''

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
