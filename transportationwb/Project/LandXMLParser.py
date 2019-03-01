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
Importer for LandXML files
'''

from shutil import copyfile
from xml.etree import ElementTree as etree
from transportationwb.ScriptedObjectSupport import Units

XML_META_KEYS = ['name', 'staStart', 'desc', 'state']
XML_STATION_KEYS = ['staAhead', 'staBack', 'staInternal', 'staIncrement', 'desc']
XML_CURVE_KEYS = ['rot', 'dirStart', 'dirEnd', 'staStart', 'radius']
XML_NAMESPACE = {'v1.2': 'http://www.landxml.org/schema/LandXML-1.2'}

def _validate_units(units):
    '''
    Validate the units of the alignment, ensuring it matches the document
    '''

    if units is None:
        print('Missing units')
        return False

    xml_units = units[0].attrib['linearUnit']

    if xml_units != Units.get_doc_units()[1]:
        print('Document units of ', Units.get_doc_units()[1], ' expected, units of ', xml_units, 'found')
        return False

    return True

def _is_float(num):
    '''
    Returns true if value is a float
    '''

    num_list = num

    if not type(num) is list:
        num_list = [num]

    for _x in num_list:

        try:
            float(_x)
        except:
            return False

    return True

def _validate_alignments(alignments):
    '''
    Validate the alignments in the XML file, ensuring the minimum data is found
    '''

    if alignments is None:
        print('Missing alignments')
        return False

    _err = []

    for alignment in alignments:

        align_name = alignment.attrib['name']

        if not all(_e in alignment.attrib for _e in XML_META_KEYS[:2]):
            _err.append('Incomplete alignment attributes found for ' + align_name)

        coord_geo = alignment.find('v1.2:CoordGeom', XML_NAMESPACE)
        sta_eqs = alignment.findall('v1.2:StaEquation', XML_NAMESPACE)

        for sta_eq in sta_eqs:

            if not all(_e in sta_eq.attrib for _e in XML_STATION_KEYS[:2]):
                _err.append('Missing back / ahead station equation data for ' + align_name)

            print([sta_eq.attrib['staBack'], sta_eq.attrib['staAhead']])
            if not _is_float([sta_eq.attrib['staBack'], sta_eq.attrib['staAhead']]):
                _err.append('Invalid back / ahead station equation data for ' + align_name)

        if coord_geo is None:
            _err.append('Missing CoordGeom for ' + align_name)

        if not coord_geo:
            _err.append('Missing curve data for ' + align_name)

        curve_idx = 0

        if coord_geo:

            for curve in coord_geo:

                curve_idx += 1

                if not all(_e in curve.attrib for _e in XML_CURVE_KEYS):
                    _err.append('Missing curve attributes for cuve ' + str(curve_idx) + ' in ' + align_name)

                if not curve:
                    _err.append('Missing PI for curve ' + str(curve_idx) + ' in ' + align_name)
                    continue

                values = curve[0].text.replace('\n', '')
                values = list(filter(None, values.split(' ')))

                if not _is_float(values):
                    _err.append('Invalid or missing PI coordinates for curve ' + str(curve_idx) + ' in ' + align_name)

    print(_err)

    return len(_err) > 0

def _parse_meta_data(alignments):
    '''
    Parse the alignment elements and strip out meta data for each alignment, returning it as a dictionary
    '''

    result = {}

    for alignment in alignments:

        for key in XML_META_KEYS:

            result[key] = alignment.attrib.get(key)

    return result

def _parse_station_data(alignments):
    '''
    Parse the alignment data to get station equations and return a dictionary
    '''

    result = {}

    for alignment in alignments:

        sta_eqs = alignment.findall('v1.2:staEquation', XML_NAMESPACE)

        for sta_eq in sta_eqs:

            for key in XML_STATION_KEYS:

                result[key] = sta_eq.attrib.get(key)

    return result

def _parse_curve_data(alignments):
    '''
    Parse the alignment data to get curve information and return as a dictionary
    '''

    result = {}

    for alignment in alignments:

        curves = alignment.findall('v1.2:Curve', XML_NAMESPACE)

        for curve in curves:

            for key in XML_CURVE_KEYS:

                result[key] = curve.attrib.get(key)

        #spirals = alignment.findall('v1.2:Spiral', XML_NAMESPACE)

    return result

def _merge_dictionaries(meta, station, curve):
    '''
    Merge the three dictionaries into one, preserving alignment structure
    '''

    result = {}

    for key in curve.keys():
        result[key] = {'meta': meta[key], 'station': station[key], 'curve': curve[key]}

    return result

def import_model(filepath):
    '''
    Import a LandXML and build the Python dictionary fronm the appropriate elements
    '''

    doc = etree.parse(filepath)
    root = doc.getroot()
    alignments = root.find('v1.2:Alignments', XML_NAMESPACE)

    for child in root:
        print(child.tag)

    if not _validate_units(root.find('v1.2:Units', XML_NAMESPACE)):
        return None

    if not _validate_alignments(alignments):
        return None

    meta_data = _parse_meta_data(alignments)

    station_data = _parse_station_data(alignments)

    curve_data = _parse_curve_data(alignments)

    return _merge_dictionaries(meta_data, station_data, curve_data)

def _write_meta_data(data, tree):
    '''
    Write out the meta data into the internal XML file
    '''

    pass

def _write_station_data(data, tree):
    '''
    Write out the station data into the internal XML file
    '''

    pass

def _write_curve_data(data, tree):
    '''
    Write out the alignment / curve data into the internal XML file
    '''

    pass

def write_file(data, tree, target):
    '''
    Write the data to a land xml file in the target location
    '''

    #_write_meta_data(data['meta'], )
    #_write_station_data(data['station'])
    #_write_curve_data(data['curve'])

    pass

def export_file(source, target):
    '''
    Export a LandXML file
    source - The source filepath (the transient LandXML file)
    target - The target datapath external to the FCStd
    '''

    copyfile(source, target)
