
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
Feature Python Object which manages XML document reading, writing, and updating
'''
import FreeCAD as App
import Part
from transportationwb.ScriptedObjectSupport import Properties
from transportationwb.XML import AlignmentImporter, AlignmentExporter
from xml.etree import ElementTree as etree

_CLASS_NAME = 'XmlFpo'
_TYPE = 'App::FeaturePython'

__title__ = _CLASS_NAME + '.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"

def create(parent=None):
    '''
    Class construction method
    parent - Optional.  Reference to existing DocumentObjectGroup.  Defaults to ActiveDocument
    '''

    _obj = None
    _name = 'Document_Data'

    result = App.ActiveDocument.get(_name)

    if (result):
        return result

    if parent:
        _obj = parent.newObject(_TYPE, _name)
    else:
        _obj = App.ActiveDocument.addObject(_TYPE, _name)

    result = _XmlFpo(_obj)

    _obj.ViewObject.Proxy = 0

    return result

class _XmlFpo():
    '''
    Class provides basic support for XML datasets stored internally in the FCStd.

    XML files are loaded when requested by FPO's that ened them and stored here.
    Requesting FPO's can access the data from a dictionary entry and push updated data back.
    Reads from the internal transient XML are done by calling the read() method
    Writes to the internal transient XML's are done by calling the write() method

    The class provides 'App::PropertyFileIncluded' properties for the internal XML files to ensure
    they are serialized on document saves
    '''

    XML_ID = ['alignment']
    XML_IO = {'alignment': {'import': AlignmentImporter.AlignmentImporter(), 'export': AlignmentExporter.AlignmentExporter()}}

    def __init__(self, obj):
        '''
        Main class intialization
        '''

        self.Enabled = False
        self.Type = "_" + _CLASS_NAME
        self.Object = obj
        self.last_action = {'alignment': None}
        self.data = {}

        for _id in self.XML_ID:
            self.data[_id] = {}
    
        self.template_path = 'data/landXML-imperial-template.xml'

        if Units.is_metric_doc():
            self.template_path = 'data/landXML-metric-template.xml'

        obj.Proxy = self

        #add class properties
        Properties.add(obj, 'FileIncluded', 'Alignment XML', 'Internal XML for Alignments', None, is_hidden=True)

        self.Enabled = True

    def __getstate__(self):
        '''
        State method for serialization
        '''
        return self.Type

    def __setstate__(self, state):
        '''
        State method for serialization
        '''
        if state:
            self.Type = state

    def execute(self, obj):
        '''
        Class execute for recompute calls
        '''
        pass

    def update(xml_id, key, data):
        '''
        Update the dataset for the passed xml id
        '''

        if not xml_id in self.XML_ID:
            print('Invalid XML data id')
            return

        self._lat_action(xml_id, 'update')

        self.data[xml_id][key] = data

    def read(self, xml_id):
        '''
        Read the transient xml specified in xml_id.

        See XML_ID const member for valid id's
        '''

        if not xml_id in self.XML_ID:
            print('Invalid XML data id')
            return

        if not self.last_action[xml_id] == 'read':
            self.last_action[xml_id] = 'read'
            self.data = self.importer.import_file()

        return self.data

    def write(self, xml_id):
        '''
        Write the transient xml data to the file specified by xml_id

        See XML_ID const member for valid id's
        '''

        if not xml_id in self.XML_ID:
            print('Invalid XML data id')
            return

        if not self.last_action[xml_id] == 'write':
            self.last_action[xml_id] = 'write'
            return

        tree = etree.parse(self.template_path)
        self.exporter.write(tree, self.data, App.ActiveDocument.TransientDir + '/' + xml_id + '.xml')            
