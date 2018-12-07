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
from transportationwb.corridor.alignment import HorizontalCurve, Metadata

class ImportHorizontalCurve():

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
                'MenuText': "Import Horizontal Alignment",
                'ToolTip' : "Import a Horizontal Alignment from JSON",
                'CmdType' : "ForEdit"}

    def getFile(self):
        '''
        Displays the file browser dialog to pick the JSON file
        '''
        dlg = QtGui.QFileDialog()
        options = dlg.Options()
        options |= dlg.DontUseNativeDialog
        dlg.setDefaultSuffix('.json')
        file_name, _ = dlg.getOpenFileName(dlg,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

        return file_name

    def build_alignment(self, group, data):
        '''
        Build the curve objects describing the alignemtn
        '''

        curve_list = []
        cur_curve = []
        geo = data['geometry']
        count = len(geo)

        #iterate geometry, combining curves into 1, 2, and 3 center groups
        for _x in range(0, count):

            cur_curve.append(geo[_x])

            #test the next cure in the list.  If it has no bearing, it's PC is attached to
            #the current curve's PT.
            #If the curve directions are the same, it's a multi-center curve.
            if _x < count - 1:
                next_curve = geo[_x+1]

                if next_curve['bearing'] == []:
                    if next_curve['direction'] == geo[_x]['direction']:
                        continue

            curve_list.append(cur_curve)
            cur_curve = []

        #add the curves to the document hierarchy
        for curve in curve_list:

            count = len(curve)

            curve_group = group

            if count > 1:
                curve_group = group.newObject('App::DocumentObjectGroup', 'Curve-' + str(count) + ': ' + str(curve[0]['PC_station']))

            for item in curve:

                _hc = HorizontalCurve.createHorizontalCurve(item, data['meta']['units'])
                curve_group.addObject(_hc.Object)

    def validate_heirarchy(self, _id, _units):
        '''
        Validates the alignment heirarchy, adding missing groups
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
        Executes the tangent construction.
        '''

        file_name = self.getFile()

        if file_name == '':
            return

        data = None

        with open(file_name, 'r') as json_data:
            data = json.load(json_data)

        for alignment in data:

            _id = alignment['meta']['id']
            _units = alignment['meta']['units']

            if _units.lower() in  ['english', 'british']:
                _units = _units[0].upper() + _units[1:].lower()
            else:
                print("Invalid units specified in json")
                return

            [group, meta] = self.validate_heirarchy(_id, _units)

            if group is None:
                return

            meta.set_bearing(alignment['meta']['bearing'])
            meta.set_limits(alignment['meta']['limits'])
            meta.add_station_equations(alignment['meta'].get('st_eq'))
            meta.set_reference_alignment(alignment['meta'].get('location'))

            self.build_alignment(group, alignment)

Gui.addCommand('ImportHorizontalCurve', ImportHorizontalCurve())