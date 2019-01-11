# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 microelly, Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  Based on original implementation by microelly.  See stationing.py     *
# *  for original implementation.                                          *
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
from transportationwb.corridor.template import TemplateLibrary

class ViewTemplateLibrary():
    '''
    View library class.
    Open the template library for selecting templates
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
                'MenuText': "Open Template Library",
                'ToolTip' : "Open the template library",
                'CmdType' : "ForEdit"}

    def Activated(self):

        TemplateLibrary.show()


Gui.addCommand('ViewTemplateLibrary', ViewTemplateLibrary())