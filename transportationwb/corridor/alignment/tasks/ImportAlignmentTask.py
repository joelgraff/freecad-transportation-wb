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
    def __init__(self, update_callback):

        path = sys.path[0] + '/../freecad-transportation-wb/transportationwb/corridor/alignment/tasks/import_alignment_task_panel.ui'
        self.ui = path
        self.form = None
        self.update_callback = update_callback

    def accept(self):
        self.update_callback(self)
        return True

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

    def add_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()
        index = 0

        if not indices:
            row = self.form.table_view.model().rowCount()
            self.form.table_view.model().insertRows(row, 1)
            index = self.form.table_view.model().index(row, 0)

        else:
            for index in indices:

                if not index.isValid():
                    continue

                self.form.table_view.model().insertRows(index.row(), 1)

            index = indices[0]

        self.form.table_view.setCurrentIndex(index)
        self.form.table_view.edit(index)

    def remove_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()

        for index in indices:

            if not index.isValid():
                continue

            self.form.table_view.model().removeRows(index.row(), 1)

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

            dialect = sniffer.sniff(first_bytes)
            self.form.delimiter.setText(dialect.delimiter)

            check_state = QtCore.Qt.Checked

            if not sniffer.has_header(first_bytes):
                check_state = QtCore.Qt.Unchecked

            self.form.headers.setCheckState(check_state)

            stream.seek(0)

            csv_reader = csv.reader(stream, dialect)

            #populate table view...
            data = [row for row in csv_reader]

            print('data set: ', data)
            self.form.table_model = Model(self.form.table_view, data[0], data)
            self.form.table_view.setModel(self.form.table_model)

    def setup(self):

        #convert the data to lists of lists

        _mw = self.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.add_button = form.findChild(QtGui.QPushButton, 'add_button')
        form.remove_button = form.findChild(QtGui.QPushButton, 'remove_button')
        form.table_view = form.findChild(QtGui.QTableView, 'table_view')

        form.file_path = form.findChild(QtGui.QLineEdit, 'filename')
        form.pick_file = form.findChild(QtGui.QToolButton, 'pick_file')
        form.headers = form.findChild(QtGui.QCheckBox, 'headers')
        form.delimiter = form.findChild(QtGui.QLineEdit, 'delimiter')

        form.pick_file.clicked.connect(lambda: self.choose_file())
        form.file_path.textChanged.connect(lambda: self.examine_file())
        #form.headers.clicked.connect()
        #form.delimiter.???

        form.table_model = Model(form.table_view, [], [])

        form.table_view.setModel(Model(form.table_model, [], []))
        form.table_view.setItemDelegate(Delegate())
        form.table_view.clicked.connect(lambda: form.table_view.model().sort(2))
        self.form = form

    def getMainWindow(self):

        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def addItem(self):
        pass

    def get_model(self):
        '''
        Returns the model data set with every element converted to string to external Loft object
        '''

        return self.form.table_view.model().dataset
