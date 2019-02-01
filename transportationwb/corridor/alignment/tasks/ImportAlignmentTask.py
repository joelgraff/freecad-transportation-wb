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
DESCRIPTION
'''

import sys
import csv

from PySide import QtGui, QtCore

import FreeCAD as App

from transportationwb.corridor.alignment.tasks.ImportAlignmentModel import ImportAlignmentModel as Model
from transportationwb.corridor.alignment.tasks.ImportAlignmentViewDelegate import ImportAlignmentViewDelegate as Delegate

class ImportAlignmentTask:

    combo_model = ['Northing', 'Easting', 'Bearing', 'Distance', 'Radius', 'Degree', 'ID', 'Parent_ID', 'Parent_Eq', 'Child_Eq', 'Datum']

    def __init__(self, update_callback):

        path = sys.path[0] + '/../freecad-transportation-wb/transportationwb/corridor/alignment/tasks/import_alignment_task_panel.ui'
        self.ui = path
        self.form = None
        self.update_callback = update_callback
        self.dialect = None
        self.vector_model = None
        self.vector_types = None
        self.meta_data_dict = {el:'' for el in ImportAlignmentTask.combo_model[6:]}
        self.meta_data = []

    def accept(self):

        #returns a message string for notification
        result = self.validate_headers(self.form.header_matcher.model().data_model[0])

        #no message returned = success
        if not result:
            self.import_model()
            self.update_callback({'types': self.vector_types, 'data': self.vector_model, 'metadata': self.meta_data})
            return True

        dialog = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Duplicate / Conflicting Headers', result)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.exec_()

        return False

    def reject(self):
        return True

    def clicked(self, index):
        pass

    def open(self):
        pass

    def needsFullSpace(self):
        return False

    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok)

    def helpRequested(self):
        pass

    def validate_headers(self, headers):
        '''
        Returns an empty list if header selections are valid,
        list of conflicing header tuples otherwise
        Northing / Easting cannot be selected with Distance / Bearing
        Radius cannot be selected with Degree
        '''

        #key headers to test for
        nedb = ['Northing', 'Easting', 'Distance', 'Bearing']

        #list of valid headers from the user input
        valid_items = [_i for _i in headers if _i in nedb]

        #boolean list of indices in nedb which are found in the headers
        bools = [_i in headers for _i in nedb]

        ne_bools = bools[:2]
        db_bools = bools[2:]

        #resulting message
        result = ''

        #------------
        #----TESTS---
        #------------

        #test for duplicates
        dupes = list(set([_i for _i in valid_items if valid_items.count(_i) > 1]))

        if dupes:

            result += 'Duplicates: ' + ','.join(dupes) + '\n'

        #test to seee if both northing / easting or distance / bearing are specified
        if not (all(_i for _i in ne_bools) or all(_i for _i in db_bools)):

            result += 'Incomplete Northing/Easting or Bearing/Distance\n'

        #test for conflicting headers
        lt = '/'.join(nedb[:2][_i] for _i, _v in enumerate(ne_bools) if _v)
        rt = '/'.join(nedb[2:][_i] for _i, _v in enumerate(db_bools) if _v)

        if lt and rt:

            result += lt + ' conflicts with ' + rt + '\n'

        #test to see if both curve radius and degree have been specified
        if all(_i in valid_items for _i in ['Radius', 'Degree']):

            result += 'Radius conflicts with Degree'

        return result

    def choose_file(self):
        '''
        Open the file picker dialog and open the file that the user chooses
        '''

        open_path = App.getUserAppDataDir() + 'Mod/freecad-transportation-wb/data/alignment/'

        file_name = QtGui.QFileDialog.getOpenFileName(self.form, 'Select CSV', open_path, self.form.tr('CSV Files (*.csv)'))

        if not file_name[0]:
            return

        self.form.file_path.setText(file_name[0])

    def examine_file(self):
        '''
        Examine the CSV file path indicated in the QLineEdit, testing for headers and delimiter
        and populating the QTableView
        '''

        file_path = self.form.file_path.text()

        stream = None

        try:
            stream = open(file_path)
            stream.close()

        except OSError:
            dialog = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Unable to open file ', file_path)
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.exec_()
            return
        
        sniffer = csv.Sniffer()

        with open(file_path, encoding="utf-8-sig") as stream:

            first_bytes = stream.read(1024)
            stream.seek(0)

            self.dialect = sniffer.sniff(first_bytes)
            self.form.delimiter.setText(self.dialect.delimiter)

            check_state = QtCore.Qt.Checked

            if not sniffer.has_header(first_bytes):
                check_state = QtCore.Qt.Unchecked

            self.form.headers.setCheckState(check_state)

        self.open_file()

    def open_file(self):
        '''
        Open the file for previewing
        '''

        if not self.dialect:
            self.examine_file()

        if self.dialect.delimiter != self.form.delimiter.text():
            self.dialect.delimiter = self.form.delimiter.text()


        with open(self.form.file_path.text(), encoding="utf-8-sig") as stream:

            stream.seek(0)

            csv_reader = csv.reader(stream, self.dialect)

            #populate table view...
            data = [row for row in csv_reader]

            header = data[0]

            if self.form.headers.isChecked():
                data = data[1:]
            else:
                header = ['Column ' + str(_i) for _i in range(0, len(data[0]))]

            table_model = Model('csv', header[:], data)
            self.form.table_view.setModel(table_model)


        self.populate_views(header)

    def populate_views(self, header):
        '''
        Populate the table views with the data acquired from open_file
        '''
        model = ImportAlignmentTask.combo_model[:]

        lower_header = [_x.lower() for _x in header]
        lower_model = [_x.lower() for _x in model]
        
        #get indices in model that are exact matches in header
        model_indices = [_i for _i, _v in enumerate(lower_model) if _v in lower_header]
        header_indices = [_i for _i, _v in enumerate(lower_header) if _v in lower_model]

        pairs = []

        for _i in model_indices:

            for _j in header_indices:

                if lower_model[_i] == lower_header[_j]:
                    pairs.append([_i, _j])

        top_row = [''] * len(header)

        for tpl in pairs:
            top_row[tpl[1]] = model[tpl[0]]
            
        matcher_model = Model('matcher', [], [top_row, header[:]])

        self.form.header_matcher.setModel(matcher_model)
        self.form.header_matcher.hideRow(1)
        self.form.header_matcher.setMinimumHeight(self.form.header_matcher.rowHeight(0))
        self.form.header_matcher.setMaximumHeight(self.form.header_matcher.rowHeight(0))
        self.form.header_matcher.setItemDelegate(Delegate(ImportAlignmentTask.combo_model))

        self.form.table_view.horizontalScrollBar().valueChanged.connect(self.form.header_matcher.horizontalScrollBar().setValue)

    def setup(self):

        #convert the data to lists of lists

        _mw = self.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.add_button = form.findChild(QtGui.QPushButton, 'add_button')
        form.remove_button = form.findChild(QtGui.QPushButton, 'remove_button')
        form.table_view = form.findChild(QtGui.QTableView, 'table_view')
        form.header_matcher = form.findChild(QtGui.QTableView, 'header_matcher')

        form.file_path = form.findChild(QtGui.QLineEdit, 'filename')
        form.pick_file = form.findChild(QtGui.QToolButton, 'pick_file')
        form.headers = form.findChild(QtGui.QCheckBox, 'headers')
        form.delimiter = form.findChild(QtGui.QLineEdit, 'delimiter')

        form.pick_file.clicked.connect(self.choose_file)
        form.file_path.textChanged.connect(self.examine_file)
        form.headers.stateChanged.connect(self.open_file)
        form.delimiter.editingFinished.connect(self.open_file)

        self.form = form

    def getMainWindow(self):

        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def get_model(self):
        '''
        Returns the model data set with every element converted to string to external Loft object
        '''

        result = ''

        return result

    def import_model(self):
        '''
        Import the model based on valid user-specified headers for the provided csv
        '''

        headers = self.form.header_matcher.model().data_model[0]
        csv_headers = self.form.header_matcher.model().data_model[1]

        #replace all non-valid headers in the result with blanks
        valid_headers = [_v if _v in ImportAlignmentTask.combo_model else '' for _v in headers]

        type_lists = [['Easting', 'Distance'], ['Northing', 'Bearing'], ['Degree', 'Radius']]
        metadata_list = ['ID', 'Parent_ID', 'Parent_Eq', 'Child_Eq', 'Datum']

        #save a list of the vector types corresponding to the coordinate in the App.Vector
        self.vector_types = [_v for type_list in type_lists for _v in type_list if _v in valid_headers]

        #get the vector coordinate indices, storing positional indices in x and y, and arc indices in z
        pos_x = [_i for _i, _v in enumerate(valid_headers) if _v in ['Easting', 'Distance']][0]
        pos_y = [_i for _i, _v in enumerate(valid_headers) if _v in ['Northing', 'Bearing']][0]
        arc_z = [_i for _i, _v in enumerate(valid_headers) if _v in ['Degree', 'Radius']][0]

        self.vector_model = []

        #build the data set as a list
        with open(self.form.file_path.text(), encoding="utf-8-sig") as stream:

            data = [row for row in csv.reader(stream, self.dialect)]

        #skip the first row if it's the header row
        if self.form.headers.isChecked():
            data = data[1:]

        #create indices for metadata that's provided in the csv
        metadata_indices = [(_i, _v) for _i, _v in enumerate(valid_headers) if _v in metadata_list]

        #record the x,y,z coordinates correlating to the curve position and radius
        object_idx = 0
        alignment_data = []

        dct = None

        #iterate the rows and build the model data
        for row in data:

            for tpl in metadata_indices:

                meta_data = row[tpl[0]]

                if meta_data:

                    if dct is None:
                        dct = {key: value[:] for key, value in  self.meta_data_dict.items()}

                    dct[tpl[1]] = meta_data

            if dct:
                self.meta_data.append(dct)
                dct = None

            if len(self.meta_data) - 1 > object_idx:

                self.vector_model.append(alignment_data[:])
                alignment_data = []
                object_idx += 1

            alignment_data.append(App.Vector(float(row[pos_x]), float(row[pos_y]), float(row[arc_z])))

        self.vector_model.append(alignment_data[:])
