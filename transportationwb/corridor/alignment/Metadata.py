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

'''
Manages alignment metadata
'''

__title__ = "Metadata.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Part
import transportationwb

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def createMetadata(name, units):
    '''
    Creates an alignment parameter object
    '''

    obj = App.ActiveDocument.addObject("App::FeaturePython", name + "_metadata")

    obj.Label = translate("Transportation", name + '_metadata')

    meta = _Metadata(obj)

    meta.Object.Units = units
    
    _ViewProviderMetadata(obj.ViewObject)

    return meta

class _Metadata():

    def __init__(self, obj):
        """
        Default Constructor
        """

        obj.Proxy = self
        self.Type = 'Metadata'
        self.Object = obj
        self._add_property('', 'General.Units', 'Base units of alignment', 'English', False, ['English', 'Metric'])
        self._add_property('Length', 'General.Start_Station', 'Starting station', 0.00)
        self._add_property('Length', 'General.End_Station', 'Ending station', 0.00)
        self._add_property('Length', 'General.Length', 'Length of baseline', 0.00, True)
        self._add_property('Angle', 'General.Bearing', 'Initial bearing of alignment', 0.00)
        self._add_property('String', 'General.Quadrant', 'Bearing quadrant', '')
        self._add_property('String', 'Location.Alignment', 'Name of reference alignment', '',True)
        self._add_property('Length', 'Location.Primary', 'Station position along reference alignment', 0.00)
        self._add_property('Length', 'Location.Secondary', 'Station position along local alignment', 0.00)

        self.init = True

    def set_reference_alignment(self, location):
        '''
        Sets the name and station position of the refrence alignment along which
        this alignment is located.

        location[0] - Name of reference alignment
        location[1] - Station position along reference alignment
        '''

        if location == []:
            return

        if len(location) != 3:
            print('Invalid location data: ', location)
            return

        self.Object.Alignment = location[2]
        self.Object.Secondary = str(location[0]) + "'"
        self.Object.Primary = str(location[1]) + "'"

    def set_bearing(self, bearing):
        '''
        Sets the bearing data based on passed list of three floats
        List must be in Degree-Minute-Second (DMS) format.
        Bearing quadrant (N,S,E,W) is derived from DMS value

        bearing[0:3] = [Degrees, Minutes, Seconds]
        '''

        if len(bearing) != 3:
            print("Invalid bearing data: ", bearing)
            return

        quad_list = ['NE', 'SE', 'SW', 'NW']
        quad_count = -1
        deg = bearing[0]

        while deg >= 0.0:
            deg -= 90.0
            quad_count += 1

            if quad_count > 3:
                quad_count = 0

        #if quad_count < 0:
        #    print("Invalid bearing data: ", bearing)
        #    return

        self.Object.Bearing = deg + 90.0 + bearing[1] / 60.0  + bearing[2] / 3600.0
        #self.Object.Quadrant = dir_list[dir_count]

    def set_limits(self, limits):
        '''
        Sets the project limits based on passed float tuple

        limits[0] - starting station
        limits[1] - ending station
        '''

        if len(limits) != 2:
            print("Invalid limits specified")
            return

        self.Object.Start_Station = str(limits[0]) + "'"
        self.Object.End_Station = str(limits[1]) + "'"

    def add_station_equations(self, sta_eqs):
        '''
        Adds station equations to the object.  Checks to ensure each equation hasn't already been added.

        sta_eqs - list of station equation tuples
        '''

        if not sta_eqs:
            return

        _x = 1

        st_eq_floats = []

        for st_eq in sta_eqs:
            st_eq_floats.append([float(_s) for _s in st_eq])

        for st_eq in st_eq_floats:

            _y = str(_x)
            self._add_property('FloatList', 'Station Equations.Equation_' + _y, 'Start / end tuple for station equation ' + _y, st_eq)
            _x += 1

    def _add_property(self, p_type, name, desc, default=None, isReadOnly=False, p_list=[]):
        '''
        Build FPO properties

        p_type - the Property type, either using the formal type definition ('App::Propertyxxx') or shortended version
        name - the Property name.  Groups are defined here in 'Group.Name' format.  
               If group is omitted (no '.' in the string), the entire string is used as the name and the default group is
               the object type name
        desc - tooltip description
        default_value - default property value
        isReadOnly - sets the property as read-only
        p_list - the list of possible selections (for Enumeration types only)
        '''

        tple = name.split('.')

        p_name = tple[0]
        p_group = self.Type

        if len(tple) == 2:
            p_name = tple[1]
            p_group = tple[0]

        if p_list:
            p_type = 'App::PropertyEnumeration'

        elif p_type == 'Length':
            p_type = 'App::PropertyLength'

        elif p_type == 'String':
            p_type = 'App::PropertyString'

        elif p_type == 'Bool':
            p_type = 'App::PropertyBool'

        elif p_type == 'FloatList':
            p_type = 'App::PropertyFloatList'

        elif p_type == 'Float':
            p_type = 'App::PropertyFloat'

        elif p_type == 'Angle':
            p_type = 'App::PropertyAngle'

        else:
            print ('Invalid property type specifed', p_type)
            return

        self.Object.addProperty(p_type, p_name, p_group, QT_TRANSLATE_NOOP("App::Property", desc))

        if p_list:
            setattr(self.Object, p_name, p_list)
        else:
            setattr(self.Object, p_name, default)

        if isReadOnly:
            self.Object.setEditorMode(p_name, 1)

        return

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def execute(self, fpy):

        pass

class _ViewProviderMetadata:

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

    def getIcon(self):
        return ""