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

def createMetadata(name):
    '''
    Creates an alignment parameter object
    '''

    obj = App.ActiveDocument.addObject("App::FeaturePython", name + "_metadata")

    #obj.Label = translate("Transportation", OBJECT_TYPE)
    vc = _Metadata(obj)
    
    _ViewProviderMetadata(obj.ViewObject)

    return vc

class _Metadata():

    def __init__(self, obj):
        """
        Default Constructor
        """

        obj.Proxy = self
        self.Type = 'Metadata'
        self.Object = obj
        self._add_property('String', 'General.Name', 'Alignment name', "alignment")
        self._add_property('', 'General.Units', 'Base units of alignment', 'English', False, ['English', 'Metric'])
        self._add_property('Length', 'General.Start_Station', 'Starting station for the cell', 0.00)
        self._add_property('Length', 'General.End_Station', 'Ending station for the cell', 0.00)
        self._add_property('Length', 'General.Length', 'Length of baseline', 0.00, True)

        self.init = True

    def add_station_equation(self, sta_eqs):
        '''
        Adds station equations to the object.  Checks to ensure each equation hasn't already been added.

        sta_eqs - list of station equation tuples
        '''

        _x = 1

        for st_eq in sta_eqs:
            _y = str(_x)
            self._add_property('FloatList', 'Station Equations.Equation ' + _y, 'Start / end tuple for station equation ' + _y, "st_eq1", st_eq)

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

        else:
            print ('Invalid property type specifed', p_type)
            return

        prop = self.Object.addProperty(p_type, p_name, p_group, QT_TRANSLATE_NOOP("App::Property", desc))

        if p_list:
            setattr(prop, p_name, p_list)

        #set the default value (not a reassignment)
        prop = default

        if isReadOnly:
            self.Object.setEditorMode(p_name, 1)

        return prop

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