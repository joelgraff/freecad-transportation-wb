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

    XML_COORD_GEO = {**XML_META, 
                     **{'oID': ('ObjectID', ''), 'state': ('Status', '')}
                    }

    XML_ALIGNMENT = {**XML_COORD_GEO,
                     **{'length': ('Length', 0.0), 'staStart': ('StartStation', 0.0)}
    }

    XML_GEO_META = {**XML_ALIGNMENT, 
                    **{'note': ('Note', '')}
                   }

    XML_LINE = {**XML_GEO_META, 
                **{'dir': ('BearingIn', 0.0)}
               }

    XML_ARC = {**XML_GEO_META, 
               **{'rot': ('Direction', 0.0), 'chord': ('Chrod', 0.0), 
               'crvType': ('CurveType', 'arc'), 'delta': ('Delta', 0.0),
               'dirEnd': ('BearingOut', 0.0), 'dirStart': ('BearingIn', 0.0),
               'external': ('External', 0.0), 'midOrd': ('MiddleOrdinate', 0.0),
               'radius': ('Radius', 0.0), 'staStart': ('StartStation', 0.0),
               'tangent': ('Tangent', 0.0)}
              }

    XML_SPIRAL = {**XML_ARC,
                  **{'radiusStart': ('StartRadius', 0.0), 'radiusEnd': ('EndRadius', 0.0),
                  'spiType': ('SpiralType', 'clothoid'), 'constant': ('Constant', 0.0),
                  'theta': ('Theta', 0.0), 'totalX': ('TotalX', 0.0), 'totalY': ('TotalY', 0.0),
                  'tanLong': ('LongTangent', 0.0), 'tanShort': ('ShortTangent', 0.0)}
                 }

    XML_STATION = {'staAhead': ('Ahead', 0.0), 'staBack': ('Back', 0.0),
                   'staInternal': ('InternalStation', 0.0), 'staIncrement': ('Direction', 0),
                   'desc': ('Description', '')
                  }

    def __init__(self):

        self.errors = []

    def write_meta_data(self, data, node):
        '''
        Write the project and application data to the file
        '''

        self._write_tree_data(data, LandXml.get_child(node, 'Project'), self.XML_META)

        node = LandXml.get_child(node, 'Application')

        node.set('version', ''.join(App.Version()[0:3]))
        node.set('timeStamp', datetime.datetime.utcnow().isoformat())

    def _write_tree_data(self, data, node, key_dict):
        '''
        Write data to the tree using the passed parameters
        '''

        for _k, _v in key_dict.items():

            value = data.get(_v[0])

            if value is None:
                value = _v[1]

            node.set(_k, value)

    def write_station_data(self, data, parent):
        '''
        Write station equation information for alignment
        '''

        for sta_eq in data:
            self._write_tree_data(sta_eq, parent, self.XML_STATION)

    def _write_coordinates(self, data, parent):
        '''
        Write coordinate children to parent geometry
        '''

        for _key in ['Start', 'End', 'Center', 'PI']:

            if not _key in data:
                continue

            _child = LandXml.add_child(parent, _key)

            LandXml.set_text(_child, data[_key])

    def _write_alignment_data(self, data, parent):
        '''
        Write individual alignment to XML
        '''

        _align_node = LandXml.add_child(parent, 'Alignment')

        #write the alignment attributes
        self._write_tree_data(data['meta'], _align_node, self.XML_ALIGNMENT)

        _coord_geo_node = LandXml.add_child(_align_node, 'CoordGeom')

        #write the geo coordinate attributes
        self._write_tree_data(data['meta'], _coord_geo_node, self.XML_COORD_GEO)

        #write the station equation data
        self.write_station_data(data['station'], _align_node)
        
        #write teh alignment geometry data
        for _geo in data['geometry']:

            _node = None

            if _geo['Type'] == 'line':

                _node = LandXml.add_child(_coord_geo_node, 'Curve')
                self._write_tree_data(_geo, _node, self.XML_LINE)

            elif _geo['Type'] == 'arc':

                _node = LandXml.add_child(_coord_geo_node, 'Line')
                self._write_tree_data(_geo, _node, self.XML_ARC)

            if _node:
                self._write_coordinates(_geo, _node)

    def write_alignments_data(self, data, node):
        '''
        Write all alignments to XML
        '''

        _parent = LandXml.add_child(node, 'Alignments')

        for _align in data:

            #self._write_tree_data(_align['meta'], _parent, self.XML_META)
            self._write_alignment_data(_align, _parent)

    def write(self, data):
        '''
        Write the alignment data to a land xml file in the target location
        '''

        filename = 'landXML-' + Units.get_doc_units()[1] + '.xml'

        doc = etree.parse(App.getUserAppDataDir() + 'Mod/freecad-transportation-wb/data/' + filename)
        root = doc.getroot()

        self.write_alignments_data(data, root)
    
        #self.write_meta_data(data['meta'], root)
        for _align in data:

            self.write_station_data(_align['station'], LandXml.get_child(root, 'Alignments'))

        doc.write(open(
            App.getUserAppDataDir() + 'Modfreecad-transportation-wb/data/alignments.xml', 'w'), encoding='UTF-8')
