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

class ImportVerticalCurve():

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Shift+V",
                'MenuText': "Import Vertical Alignment",
                'ToolTip' : "Import a Vertical Alignment from JSON",
                'CmdType' : "ForEdit"}

    def getFile(self):
        '''
        Displays the file browser dialog to pick the JSON file
        '''
        dlg = QtGui.QFileDialog()
        options = dlg.Options()
        options |= dlg.DontUseNativeDialog
        file_name, _ = dlg.getOpenFileName(dlg,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

        return file_name

    def build_alignment(self, group, data):
        '''
        Build the curve objects describing the alignemtn
        '''

        for vc_data in data['geometry']:

            vc_obj = VerticalCurve.createVerticalCurve(vc_data, data['alignment']['units'])
            group.addObject(vc_obj.Object)

    def validate_heirarchy(self, _id):
        '''
        Validates the alignment heirarchy, adding missing groups
        '''

        grand_parent = App.ActiveDocument.getObject('Alignments')

        if grand_parent is None:
            grand_parent = App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Alignments')

        parent = grand_parent.newObject('App::DocumentObjectGroup', _id)

        if parent is None:
            parent = App.ActiveDocument.addObject('App::DocumentObjectGroup', _id)

        group = App.ActiveDocument.getObject('VerticalCurves')

        if group is None:
            group = parent.newObject("App::DocumentObjectGroup", "Vertical Curves")

        return group

    def Activated(self):
        '''
        Executes the tangent construction.
        '''

        file_name = self.getFile()

        if file_name == '':
            return

        data = None

        with open(file_name, 'r') as json_data:
            data = json.load(json_data)

        _id = data['alignment']['id']

        group = self.validate_heirarchy(_id)

        self.build_alignment(group, data)

        parent = group.InList[0]

        meta = parent.getObject(_id + '_metadata')

        if meta is None:
            meta = Metadata.createMetadata(_id)
            parent.addObject(meta.Object)

        _x = data['alignment']['units']

        if _x.lower() in  ['english', 'british']:
            _x = _x[0].upper() + _x[1:].lower()
            meta.Object.Units = _x

        meta.Object.Name = _id
        meta.add_station_equations(data['alignment']['st_eq'])

Gui.addCommand('ImportVerticalCurve', ImportVerticalCurve())