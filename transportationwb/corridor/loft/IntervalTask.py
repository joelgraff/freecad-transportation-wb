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

from PySide import QtGui, QtCore
import operator
import re

class IntervalTask:
    def __init__(self):
        self.ui = '/home/shawty/.FreeCAD/Mod/freecad-transportation-wb/transportationwb/corridor/task_panel.ui'
        self.form = None

    def accept(self):
        print(self.form.table_view.model().dataset)
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

        for index in indices:

            if not index.isValid():
                continue

            self.form.table_view.model().insertRows(index.row(), 1)

    def remove_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()

        for index in indices:

            if not index.isValid():
                continue

            self.form.table_view.model().removeRows(index.row(), 1)

    def setupUi(self):

        _mw = self.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.add_button = form.findChild(QtGui.QPushButton, 'add_button')
        form.remove_button = form.findChild(QtGui.QPushButton, 'remove_button')

        form.table_view = form.findChild(QtGui.QTableView, 'table_view')
        form.table_view.setModel(TableModel())
        form.table_view.setItemDelegate(TableModelDelegate())

        #form.table_view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.form = form

        QtCore.QObject.connect(form.add_button, QtCore.SIGNAL('clicked()'), self.add_item)
        QtCore.QObject.connect(form.remove_button, QtCore.SIGNAL('clicked()'), self.remove_item)

    def getMainWindow(self):

        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def addItem(self):
        pass

class TableModelDelegate(QtGui.QItemDelegate):

    def createEditor(self, parent, option, index):

        return super(TableModelDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):

        text = index.data(QtCore.Qt.EditRole) or index.data(QtCore.Qt.DisplayRole)
        editor.setText(text)

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)

        self.rex_station = re.compile('[0-9]+\+[0-9]{2}\.[0-9]{2,}')
        self.rex_near_station = re.compile('(?:[0-9]+\+?)?[0-9]{1,2}(?:\.[0-9]*)?')

        self.dataset = [['0+00.00', 25], ['15+00.00', 10], ['20+00.00', 35], ['35+00.00', 50], ['60+00.00', 25]]
        self.headerdata = ['Station', 'Interval']

    def rowCount(self, parent):
        '''
        Number of rows currently in the model
        '''

        if self.dataset:
            return len(self.dataset)

        return 0

    def columnCount(self, parent):
        '''
        Number of columns currently in the model
        '''
        if self.dataset:
            return len(self.dataset[0])

        return 0

    def data(self, index, role):
        '''
        Return data for valid indices and display role
        '''
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        if not 0 <= index.row() < len(self.dataset):
            return None

        return self.dataset[index.row()][index.column()]

    def fixup_station(self, text):
        '''
        Fix up a string that is nearly a station
        '''

        value = float(text.replace('+',''))

        station = '0'

        #split the station and offset, if the station exists
        if value >= 100.0:
            station = str(int(value / 100.0))
            offset = str(round(value - float(station) * 100.0, 2))

        else:
            offset = str(value)

        print('station ', station)
        print('offset ', offset)

        offset = offset.split('.')

        #no decimals entered
        if len(offset) == 1:
            offset.append('00')

        #offset is less than ten feet
        if len(offset[0]) == 1:
            offset[0] = '0' + offset[0]

        #only one decimal entered
        if len(offset[1]) == 1:
            offset[1] += '0'

        #truncate the offset to two decimal places
        offset[1] = offset[1][:2]

        return station + '+' + offset[0] + '.' + offset[1]

    def setData(self, index, value, role):
        '''
        Update existing model data
        '''

        if role != QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.dataset):

            if index.column() == 0:

                #test to see if input is correctly formed
                rex = self.rex_station.match(value)

                if rex is None:

                    rex = self.rex_near_station.match(value)

                    #not a valid station.  Abort
                    if rex is None:
                        return False

                    #value is nearly a valid station.  Fix it up.
                    value = self.fixup_station(rex.group())

            else:

                try:
                    test = float(value)

                except:
                    return False

            self.dataset[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)

            return True

        return False

    def headerData(self, col, orientation, role):
        '''
        Headers to be displated
        '''

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headerdata[col]

        return None

    def insertRows(self, row, count, index=QtCore.QModelIndex()):
        '''
        Insert row into model
        '''

        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)

        for _x in range(count):
            self.dataset.insert(row + _x, ['',''])

        self.endInsertRows()

        return True

    def removeRows(self, row, count, index=QtCore.QModelIndex()):
        '''
        Remove row from model
        '''

        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)

        self.dataset = self.dataset[:row] + self.dataset[row + count:]

        self.endRemoveRows()

        return True

    def sort(self, Ncol, order):
        """
        Sort table by given column number.
        """
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.dataset = sorted(self.dataset, key=operator.itemgetter(Ncol))
        if order == QtCore.Qt.DescendingOrder:
            self.dataset.reverse()
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def flags(self, index):

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
