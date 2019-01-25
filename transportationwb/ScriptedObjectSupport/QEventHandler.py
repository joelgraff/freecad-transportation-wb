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

'''
Class to handle QEvents from windows / widgets
'''

from PySide import QtGui
import FreeCADGui as Gui

_CLASS_NAME = 'QEventHandler'
_TYPE = 'Part::FeaturePython'

__title__ = _CLASS_NAME + '.py'
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

def create(window_title, event_name, call_back):
    '''
    Creates a widget event handler that filters events
    on the specified widget window title
    '''

    main_window = Gui.getMainWindow()
    mdi = main_window.findChild(QtGui.QMdiArea)
    sub_windows = mdi.subWindowList()

    for item in sub_windows:

        if window_title == item.widget().windowTitle():
            return QEventHandler(item, event_name, call_back)
    
    return None


class QEventHandler(QtGui.QMainWindow):

    def __init__(self, obj, event_name, call_back):
        
        super(QEventHandler, self).__init__()

        obj.installEventFilter(self)

        self.event_name = event_name
        self.call_back = call_back

    def eventFilter(self, source, event):

        if self.event_name in str(event.type()):
            self.call_back()

        return super(QEventHandler, self).eventFilter(source, event)
