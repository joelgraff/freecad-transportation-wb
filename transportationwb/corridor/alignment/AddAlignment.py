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
from PySide import QtGui, QtCore
import transportationwb as twb
from transportationwb.corridor.alignment import Metadata, VerticalCurve

class AddAlignment():

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Shift+A",
                'MenuText': "New Alignment",
                'ToolTip' : "Add a new alignment",
                'CmdType' : "ForEdit"}

    def createAlignmentGroup(self, alignment_name):

        parent = App.ActiveDocument.getObject("Alignments")

        if parent is None:
            parent = App.ActiveDocument.addObject("App::DocumentObjectGroup", 'Alignments')

        obj = parent.newObject("App::DocumentObjectGroup", alignment_name)

        meta_obj = Metadata.createMetadata(alignment_name + "metadata")

        App.ActiveDocument.recompute()
        obj.addObject(meta_obj.Object)
        return obj

    def Activated(self):
        """
        Executes the tangent construction.
        """

        dlg = QtGui.QInputDialog()
        dlg.setWindowTitle("New Alignment")
        dlg.setLabelText('Enter alignment name:')
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)
        dlg.exec_()

        if dlg.result() == False:
            return

        if dlg.textValue() == '':
            return

        grp = self.createAlignmentGroup(dlg.textValue())

Gui.addCommand('AddAlignment', AddAlignment())