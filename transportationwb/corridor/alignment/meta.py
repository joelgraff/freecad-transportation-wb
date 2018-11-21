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

    meta = Meta(obj)
    ViewProviderMeta(meta.ViewObject)
    App.ActiveDocument.recompute()

    return meta

class _Meta:

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = "Meta"
        self.Object = obj

        #self.add_property("App::PropertyLength", "StartStation", "Starting station for the cell").StartStation = 0.00
        #self.add_property("App::PropertyLength", "EndStation", "Ending station for the cell").EndStation = 0.00
        #self.add_property("App::PropertyLength", "Length", "Length of baseline").Length = 0.00
        #obj.setEditorMode("Length", 1)

        #self.add_property("App::PropertyVectorList", "StationEquations", "Sketch containing sweep path").StationEquations = []
        #self.add_property("Part::PropertyGeometryList", "PathGeometry", "Path geometry shape").PathGeometry = []
        #self.add_property("App::PropertyLink", "SweepTemplate", "Sketch containing sweep template").SweepTemplate = None

        self.init = True

        #self.Object.StationEquations = [App.Vector(133115.8, 1000.0, 0.0), App.Vector(2500.48, 148036.76, 0.0)]

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def execute(self, fpy):

        pass

class _ViewProviderMeta:
    def __init__(self, obj):
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None         