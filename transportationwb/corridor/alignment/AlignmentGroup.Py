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

'''
Alignment DocumentObjectGroupPython class for highway alignments
'''

__title__ = "AlignmentGroup.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App

from transportationwb.ScriptedObjectSupport import Properties

def create(group_name):
    '''
    Constructor method for alignment group
    '''

    #return an existing instance of the same name, if found
    obj = App.ActiveDocument.getObject(group_name)

    if obj:
        return obj.Proxy

    obj = App.ActiveDocument.addObject("App::DocumentObjectGroupPython", group_name)

    fpo = _AlignmentGroup(obj)
    _ViewProviderAlignmentGroup(obj.ViewObject)

    return fpo

class _AlignmentGroup():

    def __init__(self, obj):

        obj.Proxy = self
        self.Type = "_AlignmentGroup"
        self.Object = obj

        Properties.add(obj, 'String', 'ID', 'Alignment group name', '')
        Properties.add(obj, 'String', 'Description', 'Alignment group description', '')

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def _get_child(self, object_type):

        for obj in self.Object.Group:
            if obj.TypeId == object_type:
                return obj

        return None

    def execute(self, obj):
        pass

class _ViewProviderAlignmentGroup(object):

    def getIcon(self):
        return ''

    def __init__(self,vobj):
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self,vobj):

        self.Object = vobj.Object
        return

    def claimChildren(self):
        return self.Object.Group

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def setEdit(self,vobj,mode=0):
        return True

    def unsetEdit(self,vobj,mode=0):
        return False

    def doubleClicked(self,vobj):
        pass

    def setupContextMenu(self, obj, menu):
        pass

    def edit(self):
        pass