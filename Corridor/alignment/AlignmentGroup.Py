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

from Project.Support import Properties, Units
from Project.ProjectObserver import ProjectObserver
from Project.XML.AlignmentExporter import AlignmentExporter

def get(grp_id=''):
    '''
    Find the existing alignments object
    '''

    return App.ActiveDocument.getObject('Alignments')

def create():
    '''
    Factory method for alignment group
    '''

    #return an existing instance of the same name, if found
    obj = App.ActiveDocument.getObject('Alignments')

    if obj:
        return obj.Proxy

    obj = App.ActiveDocument.addObject("App::DocumentObjectGroupPython", 'Alignments')

    fpo = _AlignmentGroup(obj)
    _ViewProviderAlignmentGroup(obj.ViewObject)

    return fpo

class _AlignmentGroup():

    def __init__(self, obj):

        obj.Proxy = self
        self.Type = "AlignmentGroup"
        self.Object = obj

        Properties.add(obj, 'String', 'ID', 'Alignment group name', '',
                       is_read_only=True)

        Properties.add(obj, 'String', 'Description', 'Alignment group description', '',
                       is_read_only=True)

        Properties.add(obj, 'FileIncluded', 'Xml_Path', '', '', is_hidden=True)

        ProjectObserver.get(App.ActiveDocument).register('StartSaveDocument', self.write_xml)


    def onDocumentRestored(self, fp):
        '''
        Restore object references on reload
        '''

        ProjectObserver.get(App.ActiveDocument).register('StartSaveDocument', self.write_xml)

    def write_xml(self):
        '''
        Serialize the object data and it's children to xml files
        '''

        _list = []

        #iterate the list of children, acquiring their data sets
        #and creating a total data set for alignments.
        for _obj in self.Object.OutList:
            _list.append(_obj.Proxy.get_geometry())

        exporter = AlignmentExporter()

        template_path = App.getUserAppDataDir() + 'Mod/freecad-transportation-wb/Resources/data/'
        template_file = 'landXML-' + Units.get_doc_units()[1] + '.xml'

        xml_path = App.ActiveDocument.TransientDir + '/alignment.xml'

        print('writing xml...')
        exporter.write(_list, template_path + template_file, xml_path)

        self.Object.Xml_Path = xml_path

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