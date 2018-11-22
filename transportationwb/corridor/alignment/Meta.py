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

"""
Manages algignment metadata
"""
__title__ = "Meta.py"
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

def createMeta(meta_name):
    """
    Creates an alignment metadata object
    """

    obj = App.ActiveDocument.addObject("App::FeaturePython", "Meta")

    #obj.Label = translate("Transportation", OBJECT_TYPE)
    meta = _Meta(obj)
    
    _ViewProviderMeta(obj.ViewObject)

    return meta

class _Meta():

    OBJECT_TYPE = "Meta"

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = "Meta"
        self.Object = obj

        self.add_property("App::PropertyLength", "StartStation", "Starting station for the cell", "General").StartStation = 0.00
        self.add_property("App::PropertyLength", "EndStation", "Ending station for the cell", "General").EndStation = 0.00
        self.add_property("App::PropertyLength", "Length", "Length of baseline", "General", True).Length = 0.00

        self.add_property("Part::PropertyGeometryList", "PathGeometry", "Path geometry shape", "Geometry").PathGeometry = []
        self.add_property("App::PropertyLink", "SweepTemplate", "Sketch containing sweep template", "Geometry").SweepTemplate = None

        self.init = True

    def add_property(self, prop_type, prop_name, prop_desc, group_name=OBJECT_TYPE, isReadOnly=False):

        prop = self.Object.addProperty(prop_type, prop_name, group_name, QT_TRANSLATE_NOOP("App::Property", prop_desc))

        if isReadOnly:
            prop.setEditorMode(prop_name, 1)

        return prop        

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def execute(self, fpy):

        pass

class _ViewProviderMeta:

    def __init__(self, obj):
        """
        Initialize the box culvert view provider
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