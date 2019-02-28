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
from lxml import etree
from transportationwb.ScriptedObjectSupport import Units

LXML_META_KEYS = ['name', 'staStart', 'desc', 'state']
LXML_STATION_KEYS = ['staAhead', 'staBack', 'staInternal', 'staIncrement', 'desc']
LXML_CURVE_KEYS = ['rot', 'dirStart', 'dirEnd', 'staStart', 'radius']

def _validate_units(units):
    '''
    Validate the units of the alignment, ensuring it matches the document
    '''

    return units[0].attrib['linearUnit'] == Units.get_doc_units()[1]

def _parse_meta_data(alignments):
    '''
    Parse the alignment elements and strip out meta data for each alignment, returning it as a dictionary
    '''

    result = {}

    for alignment in alignments:

        for key in LXML_META_KEYS:

            result[key] = alignment.attrib.get[key]

    return result

def _parse_station_data(alignments):
    '''
    Parse the alignment data to get station equations and return a dictionary
    '''

    result = {}

    for alignment in alignments:

        sta_eqs = alignment.findAll('staEquation')

        for sta_eq in sta_eqs:

            for key in LXML_STATION_KEYS:

                result[key] = sta_eq.attrib.get[key]

    return result

def _parse_curve_data(alignments):
    '''
    Parse the alignment data to get curve information and return as a dictionary
    '''

    result = {}

    for alignment in alignments:

        curves = alignment.findAll('Curve')

        for key in LXML_CURVE_KEYS:

            result[key] = curves.attrib.get[key]

        spirals = alignment.findAll('Spiral')

    return result

def _merge_dictionaries(meta, station, curve):
    '''
    Merge the three dictionaries into one, preserving alignment structure
    '''

    result = {}

    for key in curve.keys():
        result[key] = {'meta': meta[key], 'station': station[key], 'curve': curve[key]}

    return result

def import_file(filepath):
    '''
    Import a LandXML and build the Python dictionary fronm the appropriate elements
    '''

    doc = etree.parse(filepath)

    if not _validate_units(doc.find('Units')):
        print('Alignment data must be in units of ', Units.get_doc_units()[2])
        return None

    alignments = doc.findAll('Alignment')

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

    _write_meta_data(data['meta'], )
    _write_station_data(data['station'])
    _write_curve_data(data['curve'])

def export_file(source, target):
    '''
    Export a LandXML file
    source - The source filepath (the transient LandXML file)
    target - The target datapath external to the FCStd
    '''

    copyfile(source, target)
