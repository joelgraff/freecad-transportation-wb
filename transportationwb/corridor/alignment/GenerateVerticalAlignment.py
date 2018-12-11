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

import FreeCAD as App
import FreeCADGui as Gui
import os
import json
from PySide import QtGui
from PySide import QtCore
from transportationwb.corridor.alignment import VerticalCurve, Metadata

class GenerateVerticalAlignment():

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Shift+H",
                'MenuText': "Generate Vertical Alignment",
                'ToolTip' : "Generate the Vertical Alignment from an Alignment group",
                'CmdType' : "ForEdit"}

    def build_alignment(self, curves):
        '''
        Generate the horizontal alignment
        '''


    def validate_heirarchy(self):
        '''
        Validates the alignment heirarchy
        '''

        grand_parent = App.ActiveDocument.getObject('Alignments')

        if grand_parent is None:
            grand_parent = App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Alignments')

        #replace non-printable characters with underscore
        for _x in [' ', '.', '+', '(', ')']:
            _id = _id.replace(_x, '_')

        parent = grand_parent.newObject('App::DocumentObjectGroup', _id)

        if parent is None:
            parent = App.ActiveDocument.addObject('App::DocumentObjectGroup', _id)

        group = App.ActiveDocument.getObject('Horizontal_' + _id)

        if group is None:
            group = parent.newObject("App::DocumentObjectGroup", 'Horizontal_' + _id)

        meta = parent.getObject('metadata_' + _id)

        if meta is None:
            meta = Metadata.createMetadata(_id, _units)
            parent.addObject(meta.Object)
        else:
            if meta.Object.Units != _units:
                print("Unit mismatch")
                return [None, None]

        return [group, meta]

    def Activated(self):
        '''
        Generate the horizontal alignment
        '''

        pass

Gui.addCommand('GenerateVertialAlignment', GenerateVerticalAlignment())