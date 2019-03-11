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
Importer for Alignments in LandXML files
'''

from shutil import copyfile
from xml.etree import ElementTree as etree

import FreeCAD as App

from transportationwb.ScriptedObjectSupport import Units, LandXml
from transportationwb.ScriptedObjectSupport.Const import Const

class XmlKeyMaps(Const):

    XML_META_KEYS = {'name': 'ID', 'staStart': 'StartStation', 'desc': 'Description', 'state': 'Status', 'length': 'Length', 'units': 'Units'}
    XML_META_TYPES = {'name': 'string', 'staStart': 'float', 'desc': 'string', 'state': 'string', 'length': 'float', 'units': 'string'}
    XML_STATION_KEYS = {'staAhead': 'Ahead', 'staBack': 'Back', 'staInternal': 'Position', 'staIncrement': 'Direction', 'desc': 'Description'}
    XML_STATION_TYPES = {'staAhead': 'float', 'staBack': 'float', 'staInternal': 'float', 'staIncrement': 'int', 'desc': 'string'}
    XML_CURVE_KEYS = {}
    XML_CURVE_KEYS_TYPES = {}
    XML_CURVE_KEYS_OPT = {}
    XML_CURVE_KEYS_OPT_TYPES = {}

    XML_CURVE_KEYS['arc'] = {'rot':'Direction', 'dirStart': 'InBearing', 'dirEnd': 'OutBearing', 'staStart': 'PcStation', 'radius': 'Radius'}
    XML_CURVE_KEYS_TYPES['arc'] = {'rot': 'string', 'dirStart': 'float', 'dirEnd': 'float', 'staStart': 'float', 'radius': 'float'}
    XML_CURVE_KEYS_OPT['arc'] = {'chord': 'Chord', 'delta': 'Delta', 'external': 'External', 'length': 'Length', 'midOrd': 'MiddleOrd', 'tangent': 'Tangent'}
    XML_CURVE_KEYS_OPT_TYPES['arc'] = {'chord': 'float', 'delta': 'float', 'external': 'float', 'length': 'float', 'midOrd': 'float', 'tangent': 'float'}
    XML_CURVE_KEYS['spiral'] = {'rot': 'Direction', 'dirStart': 'InBearing', 'dirEnd': 'OutBearing', 'staStart': 'PcStation', 'radiusStart': 'Radius', 'length': 'Length'}
    XML_CURVE_KEYS_TYPES['spiral'] = {'rot': 'string', 'dirStart': 'float', 'dirEnd': 'float', 'staStart': 'float', 'radius': 'float', 'length': 'float'}
    XML_CURVE_KEYS_OPT['spiral'] = {{'chord': 'Chord', 'theta': 'Delta', 'constant': 'Constant', 'desc': 'Description', 'totalX': 'TotalX', 'totalY': 'TotalY', 'tanLong': 'Tangent', 'tanShort': 'InternalTangent'}}
    XML_CURVE_KEYS_OPT_TYPES['spiral'] = {{'chord': 'float', 'theta': 'float', 'constant': 'float', 'totalX': 'float', 'totalY': 'float', 'tanLong': 'float', 'tanShort': 'float'}}

    #A line is simply a curve with zero radius.  It's direction is the out-going bearing, it's PI is the starting point
    XML_LINE_KEYS = {'dir': 'OutBearing','length': 'Length', 'staStart': 'PcStation'}
    XML_LINE_KEYS_TYPES = {'dir': 'float', 'length': 'float', 'staStart': 'float'}

class AlignmentImporter(object):
    '''
    LandXML parsing class for alignments
    '''

    def __init__(self):

        self.errors = []
        self.maps = XmlKeyMaps()

    def _validate_units(self, units):
        '''
        Validate the units of the alignment, ensuring it matches the document
        '''

        if units is None:
            print('Missing units')
            return ''

        xml_units = units[0].attrib['linearUnit']

        if xml_units != Units.get_doc_units()[1]:
            self.errors.append('Document units of ' + Units.get_doc_units()[1] + ' expected, units of ' + xml_units + 'found')
            return ''

        return xml_units

    def _validate_alignments(self, alignments):
        '''
        Validate the alignments in the XML file, ensuring the minimum data is found
        '''

        if alignments is None:
            self.errors.append('Missing alignments')
            return False

        for alignment in alignments:

            align_name = alignment.attrib['name']

            if not all(_key in alignment.attrib for _key in list(self.maps.XML_META_KEYS.keys())[:2]):
               self.errors.append('Incomplete alignment attributes found for ' + align_name)

            coord_geo = LandXml.get_child(alignment, 'CoordGeom')
            sta_eqs = LandXml.get_children(alignment, 'StaEquation')

            for sta_eq in sta_eqs:

                if not all(_key in sta_eq.attrib for _key in list(self.maps.XML_STATION_KEYS.keys())[:2]):
                    self.errors.append('Missing back / ahead station equation data for ' + align_name)

                if not LandXml.is_float([sta_eq.attrib['staBack'], sta_eq.attrib['staAhead']]):
                    self.errors.append('Invalid back / ahead station equation data for ' + align_name)

            if coord_geo is None:
                self.errors.append('Missing CoordGeom for ' + align_name)

            if not coord_geo:
                self.errors.append('Missing curve data for ' + align_name)

            curve_idx = 0

            if coord_geo:

                for curve in coord_geo:

                    curve_idx += 1

                    if not all(_key in curve.attrib for _key in list(self.maps.XML_CURVE_KEYS.keys())):
                        self.errors.append('Missing curve attributes for cuve ' + str(curve_idx) + ' in ' + align_name)

                    if not curve:
                        self.errors.append('Missing PI for curve ' + str(curve_idx) + ' in ' + align_name)
                        continue

                    values = LandXml.get_float_list(curve[0].text)

                    if not LandXml.is_float(values):
                        self.errors.append('Invalid or missing PI coordinates for curve ' + str(curve_idx) + ' in ' + align_name)

        return len(self.errors) == 0

    @staticmethod
    def _convert_token(value, typ):
        '''
        Converts a string token to a float or integer value as indicated by type
        Returns None if fails
        value = string token
        typ = numeric type: 'float' or 'int'
        '''

        if not value:
            return None

        if typ == 'int':
            return Utils.to_int(value)
        elif typ == 'float':
            return Utils.to_float(value)

        return None
        
    def _parse_meta_data(self, alignments):
        '''
        Parse the alignment elements and strip out meta data for each alignment, returning it as a dictionary
        '''

        result = {}

        for alignment in alignments:

            align_name = alignment.attrib.get('name')
            attribs = alignment.attrib
            result[align_name] = {}

            for key, value in self.maps.XML_META_KEYS.items():

                typ = maps.XML_META_KEYS[key]:
                attr_val = self._convert_token(attribs.get(key), typ)

                if not attr_val:
                    self.errors.append('Missing or invalid %s attrubte in alignment %s' % (typ, alilgn_name))

                else:
                    result[align_name][value] = attribs.get(key)

        return result

    @staticmethod
    def _build_tuple_station_key(back, ahead):
        '''
        Convert a station string to a floating point value,
        returning none if it contains invalid characters
        '''

        _b = back.replace('+', '')
        _a = ahead.replace('+', '')

        if _b == '':
            _b = '0.0'

        if _a == '':
            _a = '0.0'

        try:
            float(_b)
            float(_a)
        except:
            return None

        return (float(_b), float(_a))

    def _parse_station_data(self, alignments):
        '''
        Parse the alignment data to get station equations and return a dictionary

        Station equations are stored in a sub-dictionary for each alignment keyed to the alignment name.
        Each sub-dictionary item is another dictionary keyed to the station equation attributes.
        Each sub-dictioanry item is keyed in the main dictionary with a tuple of the back / forward stations.

        Thus: station_data['align_name'][-1]['desc'] = description of last station equation in the specified alignment
        '''

        result = {}

        for alignment in alignments:

            align_name = alignment.attrib.get('name')
            result[align_name] = {}

            sta_eqs = LandXml.get_children(alignment, 'StaEquation')

            for sta_eq in sta_eqs:

                attribs = sta_eq.attrib

                back_sta = attribs.get('staBack')
                ahead_sta = attribs.get('staAhead')

                if back_sta is None or ahead_sta is None:
                    self.errors.append('Missing station equation data for %s: %s, %s' % (align_name, back_sta, ahead_sta))
                    continue

                tuple_key = self._build_tuple_station_key(back_sta, ahead_sta)

                if tuple_key is None:
                    self.errors.append('Invalid station equation for %s: %s, %s' % (align_name, back_sta, ahead_sta))
                    continue

                result[align_name][tuple_key] = {}

                for key, value in self.maps.XML_STATION_KEYS.items():

                    typ = maps.XML_STATION_KEYS[key]:
                    attr_val = self._convert_token(attribs.get(key), typ)

                    if not attr_val:
                        self.errors.append('Missing or invalid %s attrubte in alignment %s' % (typ, alilgn_name))

                    else:
                        result[align_name][tuple_key][value] = attribs.get(key)

        return result

    def _parse_curve_data(self, align_name, curves, curve_type = 'arc'):
        '''
        Parse curve data.  Returns a list of dictionaries describing:

        - curve PI coordinates
        - curve attributes
        - geometry type (curve)
        '''

        if not curves:
            return None

        result = []

        for curve in curves:

            result.append({'type': curve_type})

            attribs = curve.attrib

            _pi = LandXml.get_child(curve, 'PI')
            _start = LandXml.get_child(curve, 'Start')
            _center = LandXml.get_child(curve, 'Center')
            _end = LandXml.get_child(curve, 'End')

            #required attributes - skip curve if any are missing
            for key, value in self.maps.XML_CURVE_KEYS[curve_type].items():

                typ = maps.XML_CURVE_KEYS[curve_type][key]:
                attr_val = self._convert_token(attribs.get(key), typ)

                if not attr_val:
                    self.errors.append('Missing or invalid %s attribute in alignment %s' % (typ, alilgn_name))

                else:
                    result[-1][value] = attr_val

            #optional attributes
            for key, value in self.maps.XML_CURVE_KEYS_OPT[curve_type].items():

                    typ = maps.XML_CURVE_OPT_KEYS[curve_type][key]:
                    attr_val = self._convert_token(attribs.get(key), typ)

                    if not attr_val:
                        self.errors.append('Missing or invalid %s attribute in alignment %s' % (typ, alilgn_name))

                    else:
                        result[-1][value] = attribs.get(key)

            if _pi is None:
                self.errors.append('No PI found for curve in %s' % align_name)

            if not _pi.text:
                self.errors.append('No coordinate information provided for PI in %s ' % align_name)

            result[-1]['PI'] = LandXml.build_vector(LandXml.get_float_list(_pi.text))

            if _start:
                result[-1]['Start'] = LandXml.build_vector(LandXml.get_float_list(_start.text))

            if _center:
                result[-1]['Center'] = LandXml.build_vector(LandXml.get_float_list(_center.text))

            if _end:
                result[-1]['End'] = LandXml.build_vector(LandXml.get_float_list(_end.text))

        return result        

    def _parse_line_data(self, align_name, lines):
        '''
        Parse line data.  Returns a list of dicitonaries describing:
        - line start / end coordinates
        - line attributes
        - geometry type 'line'
        '''

        if not lines:
            return None

        result = []

        for line in lines:

            result.append({})

            line_start = LandXml.get_child(line, 'Start')
            line_end = LandXml.get_child(line, 'End')

            if line_start is None or line_end is None:
                self.errors.append('Alignment %s missing line data' % align_name)
                continue

            attribs = line.attrib

            for key in self.maps.XML_LINE_KEYS:

                result[-1][key] = attribs.get(key)

            result[-1]['Start'] = LandXml.build_vector(line_start.split(' '))
            result[-1]['End'] = LandXml.build_vector(line_end.split(' '))
        
        result[-1]['type'] = 'line'

        return result

    def _parse_coord_geo_data(self, alignments):
        '''
        Parse the alignment data to get curve information and return as a dictionary
        Dictionary contains a list of curves for each alignment, keyed to the alignment name
        List contains a dictionary for each curve containing it's attributes and PI location
        '''

        result = {}

        for alignment in alignments:

            align_name = alignment.attrib.get('name')
            result[align_name] = []

            coord_geo = LandXml.get_child(alignment, 'CoordGeom')

            if not coord_geo:
                print('Missing coordinate geometry for ', align_name)
                continue

            curves = LandXml.get_children(coord_geo, 'Curve')
            spirals = LandXml.get_children(coord_geo, 'Spirals')
            lines = LandXml.get_children(coord_geo, 'Lines')

            if curves:
                result[align_name] = self._parse_curve_data(align_name, curves)

            if spirals:
                result[align_name] = self._parse_spiral_data(align_name, spirals)

            if lines:
                result[align_name].extend(self._parse_line_data(align_name, lines))

            #spirals, 2-center, 3-center, superelevation...

        return result

    @staticmethod
    def _merge_dictionaries(meta, station, curve):
        '''
        Merge the three dictionaries into one, preserving alignment structure
        '''

        result = {}

        for key in curve.keys():
            result[key] = {'meta': meta[key], 'station': station[key], 'curve': curve[key]}

        return result

    def import_file(self, filepath):
        '''
        Import a LandXML and build the Python dictionary fronm the appropriate elements
        '''

        doc = etree.parse(filepath)
        root = doc.getroot()

        project = LandXml.get_child(root, 'Project')
        units = LandXml.get_child(root, 'Units')
        alignments = LandXml.get_child(root, 'Alignments')

        if not units:
            self.errors.append('Missing project units')
            return None

        unit_name = self._validate_units(units)

        if not unit_name:
            self.errors.append('Invalid project units')
            return None

        if not self._validate_alignments(alignments):
            self.errors.append('Alignment validation failure')
            return None

        project_name = ''

        if not project is None:
            project_name = project.attrib['name']

        meta_data = self._parse_meta_data(alignments)
        station_data = self._parse_station_data(alignments)
        curve_data = self._parse_coord_geo_data(alignments)

        result = {}
        result['Alignments'] = self._merge_dictionaries(meta_data, station_data, curve_data)
        result['Project'] = {}
        result['Project'][self.maps.XML_META_KEYS['name']] = project_name
        result['Project'][self.maps.XML_META_KEYS['units']] = unit_name

        return result