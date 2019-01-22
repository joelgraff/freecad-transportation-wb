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

from PySide import QtCore, QtGui

class NewLoftDialog(QtGui.QDialog):

    def getNumber(self, text):
        '''
        Get the number, assuming it's float, int, or station
        '''

        #assume the text is a float, int or valid station
        result = None

        try:
            result = float(text)
        except:
            try:
                result = float(int(text))
            except:
                if '+' in text:
                    result = self.getNumber(text.replace('+', ''))

        return result

    def update_station(self, line_edit):
        '''
        Validate the data entered in the station line edit
        '''

        value = self.getNumber(line_edit.text())

        if value is None:
            msg = QtGui.QMessageBox.critical(self, self.tr('Station Error'), self.tr('Invalid station entered'))
            msg.show()
            return

        station = int(value / 100.0)
        offset = value - float(station * 100.0)

        line_edit.setText(str(station) + '+' + str('{:04.2f}').format(offset))

    def __init__(self, units, parent=None):

        super(NewLoftDialog, self).__init__(parent)

        self.setWindowTitle(self.tr('Generate New Loft'))
        self.setSizeGripEnabled(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        layout = QtGui.QGridLayout(self)
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)

        #loft name input
        layout.addWidget(QtGui.QLabel(self.tr('Name')), 0, 1)

        self.loft_name = QtGui.QLineEdit('Loft', self)
        self.loft_name.setSizePolicy(size_policy)

        layout.addWidget(self.loft_name, 0, 2, )

        #start and end stations
        layout.addWidget(QtGui.QLabel(self.tr('Station')), 1, 1)

        self.start_sta = QtGui.QLineEdit('', self)
        self.start_sta.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.start_sta.setSizePolicy(size_policy)
        self.start_sta.editingFinished.connect( lambda: self.update_station(self.start_sta))

        layout.addWidget(self.start_sta, 1, 2)

        layout.addWidget(QtGui.QLabel(self.tr('to')), 1, 3)

        self.end_sta = QtGui.QLineEdit('0', self)
        self.end_sta.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.end_sta.setSizePolicy(size_policy)
        self.end_sta.editingFinished.connect(lambda: self.update_station(self.end_sta)

        layout.addWidget(self.end_sta, 1, 4)

        #sektch template dropdown
        layout.addWidget(QtGui.QLabel(self.tr('Template')), 2, 1)
        
        self.sketch_template = QtGui.QComboBox(self)
        self.sketch_template.setSizePolicy(size_policy)

        layout.addWidget(self.sketch_template, 2, 2)

        self.sketch_local = QtGui.QCheckBox('Local Copy', self)
        self.sketch_local.setCheckState(QtCore.Qt.CheckState.Checked)

        layout.addWidget(self.sketch_local, 2, 4)

        #alignment drop down
        layout.addWidget(QtGui.QLabel(self.tr('Alignment')), 3, 1)

        self.alignment = QtGui.QComboBox(self)
        self.alignment.setSizePolicy(size_policy)

        layout.addWidget(self.alignment, 3, 2)

        #interval spinbox
        layout.addWidget(QtGui.QLabel(self.tr('Interval (%s)' % units)), 4, 1)

        self.interval = QtGui.QSpinBox(self)
        self.interval.setRange(0,100)
        self.interval.setValue(25)

        layout.addWidget(self.interval, 4, 2)

        #material dropdown
        layout.addWidget(QtGui.QLabel(self.tr('Material')), 5, 1)

        self.material = QtGui.QComboBox(self)
        self.material.addItems(['Default', 'Material 1', 'Material 2', 'Material 3'])
        self.material.setSizePolicy(size_policy)

        layout.addWidget(self.material, 5, 2)

        #buttons
        self.ok_button = QtGui.QPushButton(self.tr('&Ok'), self)
        layout.addWidget(self.ok_button, 6, 1)

        self.cancel_button = QtGui.QPushButton(self.tr('&Cancel'), self)
        layout.addWidget(self.cancel_button, 6, 4)

        self.setLayout(layout)

    def set_template_list(self, list_items):
        '''
        Set the list of sketch templates
        '''

        for item in list_items:
            self.sketch_template.addItem(item.Label, item)

    def set_alignment_list(self, list_items):
        '''
        Set the list of alignments
        '''

        for item in list_items:
            self.alignment.addItem(item.Label, item)

    def set_material_list(self, list_items):
        '''
        Set the list of available materials
        '''

        self.material.addItems(list_items)

    def get_alignment(self):
        '''
        Return the user-selected alignment
        '''

        return self.alignment.itemData(self.alignment.currentIndex())

    def get_template(self):
        '''
        Return the user-selected template
        '''

        return self.template.itemData(self.alignment.currentIndex())

    def get_material(self):
        '''
        Return the user-selected material
        '''

        pass

    def get_interval(self):
        '''
        Return the user-defined interval
        '''

        return self.interval.value()

    def get_stations(self):
        '''
        Return the station range
        '''

        return [float(self.start_sta.text()), float(self.end_sta.text())]

    def get_name(self):
        '''
        Return the user-defined name for the loft
        '''

        return self.loft_name.text()