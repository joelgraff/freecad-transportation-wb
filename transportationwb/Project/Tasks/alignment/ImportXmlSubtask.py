# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX Joel Graff <monograff76@gmail.com>                         *
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
Subtask to populate the XML dialog when an XML file is chosen for import
'''

from PySide import QtGui, QtCore

import FreeCAD as App
import FreeCADGui as Gui

from transportationwb.XML.AlignmentImporter import AlignmentImporter
from transportationwb.ScriptedObjectSupport import WidgetModel

def create(panel, filepath):

    return ImportXmlSubtask(panel, filepath)

class ImportXmlSubtask:

    def __init__(self, panel, filepath):

        self.panel = panel

        self.parser = AlignmentImporter()
        self.data = self.parser.import_file(filepath)

        for key, item in self.data.items():
            print('\n' + key + '\n')

            if isinstance(item, dict):
                for key_1, item_1 in item.items():
                    print(key_1 + '\n')
                    print(item_1)
            else:
                print(item)

        if self.parser.errors:

            for _err in self.parser.errors:
                print(_err)

        self._setup_panel()

        self.errors = []

    def _setup_panel(self):

        self.panel.projectName.setText(self.data['Project']['ID'])

        alignment_model = list(self.data['Alignments'].keys())

        widget_model = WidgetModel.create(alignment_model)

        self.panel.alignmentsComboBox.setModel(widget_model)

        self.panel.alignmentsComboBox.currentTextChanged.connect(self._update_alignment)

        self.panel.staEqTableView.clicked.connect(self._update_curve_list)

        self._update_alignment(self.panel.alignmentsComboBox.currentText())

    def _update_alignment(self, value):

        subset = self.data['Alignments'][value]

        if subset['meta'].get('StartStation'):
            self.panel.startStationValueLabel.setText(str(subset['meta']['StartStation']))

        if subset['meta'].get('Length'):
            self.panel.lengthValueLabel.setText(str(subset['meta']['Length']))

        sta_model = []

        if subset['station']:
            for st_eq in subset['station']:
                sta_model.append(st_eq['Back'], st_eq['Ahead'], st_eq['Position'])

        headers = ['Back', 'Ahead', 'Position']

        widget_model = WidgetModel.create(sta_model, headers)

        self.panel.staEqTableView.setModel(widget_model)

        curve_model = []
        #headers = list(subset['geometry'][0].keys())
        headers = ['Type', 'Direction', 'Start', 'Radius']

        for key, geo in subset['geometry'].items():

            for curve in geo:

                row = '{0:s}, {1:s}, {2:.2f}, {3:.2f}'.format(
                    curve['Type'], curve['Direction'], curve['StartStation'], curve['Radius']
                )
                curve_model.append(row.split(','))

        print(curve_model)
        widget_model_2 = WidgetModel.create(curve_model, headers)

        self.panel.curveTableView.setModel(widget_model_2)

    def _update_curve_list(self, value):

        print('update curve list with: ', value)

    def import_model(self):

        return self.data
