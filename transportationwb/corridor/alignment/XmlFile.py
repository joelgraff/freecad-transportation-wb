# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX AUTHOR_NAME <AUTHOR_EMAIL>                         *
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
Class for managing Alignment XML file 
'''

import FreeCAD as App

from xml.etree import ElementTree as etree

from transportationwb.ScriptedObjectSupport import Units
from transportationwb.Project.AlignmentXmlImporter import AlignmentXmlImporter
from transportationwb.Project.AlignmentXmlExporter import AlignmentXmlExporter

_CLASS_NAME = 'XmlFile'

__title__ = _CLASS_NAME + '.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"

class _XmlFile():
    '''
    Xml File management class
    '''

    def __init__(self, data, importer, exporter, xml_file):
        '''
        Initialize the XML file singleton
        Data consists of a dictionary of alignment objects
        '''

        self.last_action = 'init'
        self.template_path = 'data/landXML-imperial-template.xml'

        if Units.is_metric_doc():
            self.template_path = 'data/landXML-metric-template.xml'

        self.target_path = App.ActiveDocument.TransientDir + '/' + xml_file

        self.data = data
        self.importer = importer
        self.exporter = exporter

    def update(self, key, value):
        '''
        Update the dictionary
        '''

        self.last_action = 'update'
        self.data[key] = value

    def read(self):
        '''
        Read the xml file into a dictionary
        '''

        if self.last_action != 'read':
            self.last_action = 'read'
            self.data = self.importer.import_file()

        return self.data

    def write(self):
        '''
        Write the dictionary to file
        '''

        if self.last_action == 'write':
            return

        self.last_action = 'write'

        tree = etree.parse(self.template_path)
        self.exporter.write(tree, self.data, self.target_path)
