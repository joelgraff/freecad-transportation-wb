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
Exporter for Alignments in LandXML files
'''

import datetime

from shutil import copyfile
from xml.etree import ElementTree as etree

import FreeCAD as App

from transportationwb.ScriptedObjectSupport import Units
from transportationwb.XML import LandXml

class AlignmentExporter(object):
    '''
    LandXML exporting class for alignments
    '''

    XML_META = {'name': ('ID', ''), 'desc': ('Description', '')}
    XML_APPLICATION = {'version': ()}
    #XML_STATION_KEYS = {'staAhead': 'Ahead', 'staBack': 'Back', 'staInternal': 'Position', 'staIncrement': 'Direction', 'desc': 'Description'}

    def __init__(self):

        self.errors = []
        self.maps = None

    def _write_tree_data(self, data, node, key_dict):
        '''
        Write data to the tree using the passed parameters
        '''

        for _k, _v in key_dict.items():

            value = data.get(_v[0])

            if value is None:
                value = _v[1]

            node.set(_k, value)

    def _write_project_data(self, data, root):
        '''
        Write out the meta data into the internal XML file
        '''

        self._write_tree_data(data['meta'], LandXml.get_child(root, 'Project'), self.XML_META)

    @staticmethod
    def _write_application_data(root):

        node = LandXml.get_child(root, 'Application')

        node.set('version', ''.join(App.Version()[0:3]))
        node.set('timeStamp', datetime.datetime.utcnow().isoformat())

    def _write_alignment_data(self, data, parent):
        '''
        Write individual alignment to XML
        '''

        _node = LandXml.add_child(parent, 'Alignment')

    def _write_alignments_data(self, data, node):
        '''
        Write all alignments to XML
        '''

        _parent = LandXml.add_child(node, 'Alignments')

        for _align in data['geometry']:
            self._write_alignment_data(_align, _parent)

    def _write_curve_data(self, data, root):
        '''
        Write out the alignment / curve data into the internal XML file
        '''

        alignments = LandXml.get_child(root, 'Alignments')

        #build the alignment tag with it's attributes
        _attr = {}

        for key, value in self.maps.XML_META_KEYS:

            if key == 'Units':
                continue

            _attr[key] = data['meta'][value]

        alignment = etree.SubElement(alignments, 'Alignment', _attr)

        _attr = {}

        for key, value in self.maps.XML_STATION_KEYS:

            _attr[key] = data['station'][value]

        etree.SubElement(alignment, 'StaEquation', _attr)

        coord_geo = etree.SubElement(alignment, 'CoordGeom', name=_attr['name'])

        #add curves and lines
        for curve in data['curve']:

            _attr = {'crvType': 'arc'}

            if curve['type'] == 'arc':

                #assign required attributes
                for key, value in self.maps.XML_CURVE_KEYS:
                    _attr[key] = curve[value]

                #assign optional attributes
                for key, value in self.maps.XML_CURVE_KEYS_OPT:
                    _attr[key] = curve[value]

                curve_node = etree.SubElement(coord_geo, 'Curve', _attr)

                #iterate the subelements and add them, if they exist
                for vec in ['PI', 'Start', 'Center', 'End']:

                    if not curve[vec]:
                        continue

                    str_vec = ' '.join(str(curve[vec]))
                    etree.SubElement(curve_node, vec).text = str_vec

            if curve['type'] == 'line':

                #assign required attributes
                for key, value in self.maps.XML_LINE_KEYS:
                    _attr[key] = curve[value]

                curve_node = etree.SubElement(coord_geo, 'Line', _attr)

                #iterate the subelements and add them, if they exist
                for vec in ['Start', 'End']:

                    if not curve[vec]:
                        continue

                    str_vec = ' '.join(str(curve[vec]))
                    etree.SubElement(curve_node, vec).text = str_vec

    def write(self, data, target):
        '''
        Write the alignment data to a land xml file in the target location
        '''

        filename = 'landXML-' + Units.get_doc_units()[1] + '.xml'

        doc = etree.parse(App.getUserAppDataDir + '/freecad-transportation-wb/data/' + filename)
        root = doc.getroot()

        for alignment in data:
            self._write_meta_data(alignment, root)
            self._write_curve_data(alignment, root)

        tree.write(open(target, 'w'), encoding='UTF-8')

    @staticmethod
    def export_file(source, target):
        '''
        Export a LandXML file
        source - The source filepath (the transient LandXML file)
        target - The target datapath external to the FCStd
        '''

        copyfile(source, target)
