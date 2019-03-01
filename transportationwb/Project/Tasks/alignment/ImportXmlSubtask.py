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

from transportationwb.Project import LandXMLParser

def create(panel, filepath):

    return ImportXmlSubtask(panel, filepath)

class ImportXmlSubtask:

    def __init__(self, panel, filepath):

        self.panel = panel

        self.data = LandXMLParser.import_model(filepath)

        print(self.data)
        self._setup_panel()

    def _setup_panel(self):
        self.panel.alignmentsComboBox.currentTextChanged.connect(self._update_alignment)

    def _update_alignment(self, value):

        print('update alignment: ', value)