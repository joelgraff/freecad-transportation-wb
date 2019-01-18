# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 microelly, Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  Based on original implementation by microelly.  See stationing.py     *
# *  for original implementation.                                          *
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

import Draft
import Part
import os
import time
import FreeCAD as App
import FreeCADGui as Gui
from transportationwb.corridor.template import LoftGroup

class GenerateLoft():
    '''
    Sweep generation class.
    Builds a sweep based on passed template and sweep path
    '''
    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Ctrl+Alt+G",
                'MenuText': "Generate Loft",
                'ToolTip' : "Generate loft of template along a path",
                'CmdType' : "ForEdit"}

    def _validate_tree(self):
        '''
        Validate the current tree structure, ensuring Sweep document group exists
        and return the Sweeps group object
        '''

        parent = App.ActiveDocument.findObjects('App::DocumentObjectGroup', 'Lofts')
        result = None

        if parent == []:
            result = App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Lofts')
            App.ActiveDocument.recompute()
        else:
            result = parent[0]

        return result

    def Activated(self):

        parent = self._validate_tree()

        sel = Gui.Selection.getSelection()

        if len(sel) != 2:
            print ('Invalid number of objects selected.  Select a spline and sketch to perform loft')
            return

        spline = None
        sketch = None

        for obj in sel:

            if not obj.TypeId in ['Part::Part2DObjectPython', 'Sketcher::SketchObjectPython']:
                print('Invalid object type found.  Select a spline and sketch to perform loft')
                return

            if obj.TypeId == 'Part::Part2DObjectPython':
                spline = obj
            else:
                sketch = obj

        LoftGroup.createLoftGroup(parent, sketch.Label, spline, sketch)

Gui.addCommand('GenerateLoft', GenerateLoft())