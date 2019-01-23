# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
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
from PySide import QtGui
from transportationwb.corridor.loft import LoftGroup, NewLoftDialog

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

    def _dialog_updates(self, properties):
        '''
        Callback for loft dialog to pass loft properties as a dictionary
        '''

        self.loft_properties = properties

    def generate_loft(self):
        '''
        Generate the loft from the loft properties
        '''

        if self.loft_properties is None:
            print('Invalid loft properties')
            return

        _lg = LoftGroup.createLoftGroup(
            App.ActiveDocument.Lofts,
            self.loft_properties['name'],
            self.loft_properties['alignment'],
            self.loft_properties['sketch'],
            self.loft_properties['is_local']
            )

        #_lg.set_stations(self.loft_properties['stations'])
        _lg.set_interval(self.loft_properties['interval'])
        #_lg.set_material(self.loft_properties['material'])

        _lg.set_initialized()

        #_lg.regenerate()
        print('loft generated')

    def Activated(self):

        dialog = NewLoftDialog.NewLoftDialog('ft')

        align_list = []
        template_list = []

        #test to see if a template / alignment have been pre-selected
        for obj in Gui.Selection.getSelection():

            if not obj.TypeId in ['Part::Part2DObjectPython', 'Sketcher::SketchObjectPython']:
                print('Invalid object type found.  Select a spline and sketch to perform loft')
                return

            if obj.TypeId == 'Part::Part2DObjectPython':
                align_list.append(obj)
            else:
                template_list.append(obj)

        #populate the lists with all current alignments and templates
        align_folder = App.ActiveDocument.getObject('Alignments')
        template_folder = App.ActiveDocument.getObject('Templates')

        if align_folder:
            for obj in align_folder.OutList:
                align_list.append(obj)

        if template_folder:
            for obj in template_folder.OutList:
                template_list.append(obj)

        #set the dialog properties
        dialog.set_alignment_list(align_list)
        dialog.set_template_list(template_list)
        dialog.set_update_cb(self._dialog_updates)

        #show the dialog
        result = dialog.exec_()

        if self.loft_properties is None or result == QtGui.QDialog.DialogCode.Rejected:
            return

        #create the loft object, assign the data, and generate i
        self.generate_loft()

        App.ActiveDocument.recompute()

Gui.addCommand('GenerateLoft', GenerateLoft())