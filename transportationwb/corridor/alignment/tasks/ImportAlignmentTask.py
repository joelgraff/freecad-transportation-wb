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
from transportationwb.corridor.alignment import HorizontalAlignment
from transportationwb.ScriptedObjectSupport import Utils

class ImportAlignmentTask:

    def __init__(self, update_callback):

        path = sys.path[0] + '/../freecad-transportation-wb/transportationwb/corridor/alignment/tasks/import_alignment_task_panel.ui'
        self.ui = path
        self.form = None
        self.update_callback = update_callback
        self.dialect = None
        self.alignment_type = 'Horizontal'
        self.alignment_data = []
        self.errors = []

    def accept(self):

        #returns a message string for notification
        result = self.validate_headers(self.form.header_matcher.model().data_model[0])

        #no message returned = success
        if not result:

            self.import_model()

            if self.errors:

                print('Errors encountered during import:\n')
                for _e in self.errors:
                    print(_e)

            errors = []

            for _i in self.alignment_data:

                print (_i)
                result = HorizontalAlignment.create(_i, _i['meta']['ID'] + ' Horiz').errors

                if result:
                    errors += result

            if errors:
                print('Errors encountered during alignment creation:\n')

                for _e in errors:
                    print(_e)

            return True

        #message returned - notify user
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
        model = HorizontalAlignment.meta_fields + HorizontalAlignment.data_fields + HorizontalAlignment.station_fields

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
        self.form.header_matcher.setItemDelegate(Delegate(model))

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

    @staticmethod
    def is_empty_dict(dct):
        '''
        Returns true if all key values are empty
        '''

        for key, value in dct.items():
            if value:
                return False

        return True

    def _generate_indices(self):
        '''
        Generate index values for named data for the imported CSV
        '''
        #dictionary keys for the dictionary data that is used for alignment construction
        meta_keys = HorizontalAlignment.meta_fields
        data_keys = HorizontalAlignment.data_fields
        station_keys = HorizontalAlignment.station_fields

        #get headers imported from file
        headers = self.form.header_matcher.model().data_model[0]

        self.id_index = headers.index('ID')

        #find those headers in the pre-defined header lists, preserving blanks for unused columns
        meta_headers = [_v if _v in meta_keys else '' for _v in headers]
        data_headers = [_v if _v in data_keys else '' for _v in headers]
        station_headers = [_v if _v in station_keys else '' for _v in headers]

        #generate indexed lists of the headers
        meta_indices = [(_i, _v) for _i, _v in enumerate(meta_headers) if _v in headers]
        data_indices = [(_i, _v) for _i, _v in enumerate(data_headers) if _v in headers]
        station_indices = [(_i, _v) for _i, _v in enumerate(station_headers) if _v in headers]

        #reduce lists by removing empty columns, preserving original index values of the headers
        self.meta_indices = [_x for _x in meta_indices if _x[1]]
        self.data_indices = [_x for _x in data_indices if _x[1]]
        self.station_indices = [_x for _x in station_indices if _x[1]]

    def _scrape_meta(self, row):
        '''
        Scrape metadata from a row being imported
        '''

        for tpl in self.meta_indices:

            key = tpl[1]
            value = row[tpl[0]]

            if value:
                self.meta_dict[key] = value

    def _scrape_stations(self, row):
        '''
        Scrape stationing from the row being imported
        '''

        stations = [0.0, 0.0]
        parent_id = ''
        back_value = ''

        for tpl in self.station_indices:

            key = tpl[1]
            value = row[tpl[0]]

            if not value:
                continue

            if key == 'Back':
                stations[0] = value

            elif key == 'Forward':
                stations[1] = value

            elif key == 'Parent_ID':
                parent_id = value

        if stations != [0.0, 0.0]:

            #Parent_ID means it's an intersection equation
            if parent_id:
                self.station_dict[parent_id] = stations

            else:
                self.station_dict['equations'].append(stations)

    def _scrape_data(self, row):
        '''
        Scrape PI data from the row being imported
        '''

        #build the PI dictionary to capture data from the row
        pi_dict = dict.fromkeys(HorizontalAlignment.data_fields, '')

        for tpl in self.data_indices:

            key = tpl[1]
            value = row[tpl[0]]

            if value:
                pi_dict[key] = value

        #(northing / easting) or (bearing / distance) must be specified, along with
        #either radius or degree of curve
        valid_ne = all([pi_dict['Northing'], pi_dict['Easting']])
        valid_db = all([pi_dict['Bearing'], pi_dict['Distance']])
        valid_rd = pi_dict['Radius'] or pi_dict['Degree']

        valid_pos = valid_ne or valid_db

        if valid_pos and valid_rd:
            self.alignment_dict['data'].append(pi_dict)

    def _build_dictionaries(self):
        '''
        Build the self object dictionaries that are used in data scraping
        '''

        self.meta_dict = dict.fromkeys(HorizontalAlignment.meta_fields)
        self.station_dict = {'equations':[]}
        self.alignment_dict = {'meta': [], 'station': [], 'data': []}

    def _save_alignment(self):
        '''
        Save the current alignment data to the alignment dicitonary
        and reset the collecting dictionaries
        '''

        if self.is_empty_dict(self.alignment_dict):
            return

        self.alignment_dict['meta'] = self.meta_dict
        self.alignment_dict['station'] = self.station_dict
        self.alignment_data.append(self.alignment_dict)

        self._build_dictionaries()

    def import_model(self):
        '''
        Import the CSV data
        '''

        self._build_dictionaries()
        self._generate_indices()

        #build the data set as a list
        with open(self.form.file_path.text(), encoding="utf-8-sig") as stream:

            skip_header_row = self.form.headers.isChecked()

            #each row represents a PI, a station equation, or metadata for the alignment
            for row in csv.reader(stream, self.dialect):

                if skip_header_row:

                    skip_header_row = False
                    continue

                #if the ID field has a value, a new alignment has begun
                #save the current alignment and clear the dictionary
                if row[self.id_index]:
                    self._save_alignment()

                #meta data is overwritten by data in subsequent rows
                self._scrape_meta(row)

                #station equations are appended, 
                #intersection equations are added as items using the parent id
                self._scrape_stations(row)

                #scrae PI data from the row
                self._scrape_data(row)

        #final write of the data
        self._save_alignment()
