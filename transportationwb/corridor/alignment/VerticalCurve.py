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
Manages vertical curve data
'''

__title__ = "VerticalCurve.py"
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

def createVerticalCurve(data, units):
    '''
    Creates a vertical curve alignment object

    data - dictionary containg:
    'pi' - the station of the point of intersection
    'elev' - the elevation of the point of intersection
    'g1' / 'g2' - the incoming and outoign grades between VPC / VPI and VPI / VPT
    'length' - the length of the vertical curve
    '''

    obj = App.ActiveDocument.addObject("App::FeaturePython", "VerticalCurve")

    #obj.Label = translate("Transportation", OBJECT_TYPE)
    vc = _VerticalCurve(obj)

    conv = 1000.0

    if units in ['english', 'british']:
        conv = 25.4 * 12.0
    
    obj.Length = float(data['length']) * conv
    obj.PI_Station = float(data['pi'])
    obj.PI_Elevation = float(data['elevation']) * conv
    obj.Grade_In = float(data['g1'])
    obj.Grade_Out = float(data['g2'])
 
    _ViewProviderVerticalCurve(obj.ViewObject)

    return vc

class _VerticalCurve():

    def __init__(self, obj):
        """
        Default Constructor
        """

        obj.Proxy = self
        self.Type = 'VerticalCurve'
        self.Object = obj

        self._add_property('Length', 'General.PC_Station', 'Station of the vertical Point of Curvature', 0.00, True)
        self._add_property('Length', 'General.PC_Elevation', 'Elevtaion of the vertical Point of Curvature', 0.00, True)
        self._add_property('Length', 'General.PI_Station', 'Station of the vertical Point of Intersection', 0.00)
        self._add_property('Length', 'General.PI_Elevation', 'Elevtaion of the vertical Point of Intersection', 0.00)
        self._add_property('Length', 'General.PT_Station', 'Station of the vertical Point of Tangency', 0.00, True)
        self._add_property('Length', 'General.PT_Elevation', 'Elevtaion of the vertical Point of Tangency', 0.00, True)
        self._add_property('Length', 'General.Grade_In', 'Grade of tangent between VPC and VPI', 0.00)
        self._add_property('Length', 'General.Grade_Out', 'Grade of tangent beteen VPI and VPT', 0.00)        
        self._add_property('Length', 'General.Length', 'Length of the vertical curve', 0.00)
        self._add_property('Float', 'Characteristics.A', 'Absolute difference between grades', 0.00, True)
        self._add_property('Float', 'Characteristics.K', 'Rate of Curvature', 0.00, True)
        self._add_property('Bool', 'Characteristics.Equal_Tangent', 'Is this an Equal Tangent Curve?', True, True)

        self.doRecalc = False

    def _add_property(self, p_type, name, desc, default_value=None, isReadOnly=False):
        '''
        Build properties from a dictionary
        '''

        tple = name.split('.')

        if p_type == 'Length':
            p_type = 'App::PropertyLength'

        elif p_type == 'Float':
            p_type = 'App::PropertyFloat'

        elif p_type == 'Bool':
            p_type = 'App::PropertyBool'

        elif p_type == 'PropertyLink':
            p_type = 'App::PropertyLink'

        self.Object.addProperty(p_type, tple[1], tple[0], QT_TRANSLATE_NOOP("App::Property", desc))

        prop = self.Object.getPropertyByName(tple[1])

        prop = default_value

        if isReadOnly:
            self.Object.setEditorMode(tple[1], 1)

        return prop              

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def _recalc_curve(self):

        half_length = self.Object.Length / 2.0

        self.Object.PC_Station = self.Object.PI_Station - half_length
        self.Object.PT_Station = self.Object.PI_Station + half_length

        self.Object.PC_Elevation = self.Object.PI_Elevation - self.Object.Grade_In * half_length
        self.Object.PT_Elevation = self.Object.PI_Elevation + self.Object.Grade_Out * half_length

        self.Object.A = abs(self.Object.Grade_In - self.Object.Grade_Out)
        self.Object.K = self.Object.Length / self.Object.A

    def execute(self, fpy):

        self._recalc_curve()

class _ViewProviderVerticalCurve:

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