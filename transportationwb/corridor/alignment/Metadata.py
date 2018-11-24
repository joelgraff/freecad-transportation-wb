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

    obj = App.ActiveDocument.addObject("App::FeaturePython", "Metadata")

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

        self._add_property('Length', 'General.Start_Station', 'Starting station for the cell', 0.00)
        self._add_property('Length', 'General.End_Station', 'Ending station for the cell', 0.00)
        self._add_property('Length', 'General.Length', 'Length of baseline', 0.00, True)

        self.init = True      

    def _add_property(self, p_type, name, desc, default_value=None, isReadOnly=False):
        '''
        Build properties
        '''

        tple = name.split('.')

        if p_type == 'Length':
            p_type = 'App::PropertyLength'

        elif p_type == 'PropertyLink':
            p_type = 'App::PropertyLink'

        self.Object.addProperty(p_type, tple[1], tple[0], QT_TRANSLATE_NOOP("App::Property", desc))
        prop = self.Object.getPropertyByName(tple[1])
        print(tple[1])
        print(prop)

        prop = default_value

        if isReadOnly:
            self.Object.setEditorMode(tple[1], 1)

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