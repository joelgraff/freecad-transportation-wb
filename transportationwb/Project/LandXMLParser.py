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

import FreeCAD as App

from transportationwb.ScriptedObjectSupport import Units

XML_VERSION = 'v1.2'
XML_NAMESPACE = {XML_VERSION: 'http://www.landxml.org/schema/LandXML-1.2'}

def get_child(node, node_name):
    '''
    Return the first child matching node_name in node
    '''
    return node.find(XML_VERSION + ":" + node_name, XML_NAMESPACE)

def get_children(node, node_name):
    '''
    Return all children mathcing node_name in node
    '''
    return node.findall(XML_VERSION + ':' + node_name, XML_NAMESPACE)

def get_float_list(text, delimiter=' '):
    '''
    Return a list of floats from a text string of delimited values
    '''

    values = text.replace('\n', '')
    return list(filter(None, values.split(delimiter)))

def is_float(num):
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

def build_vector(coords):
    '''
    Returns an App.Vector of the passed coordinates,
    ensuring they are float-compatible
    '''

    try:
        for _c in coords:
            float(_c)
    except:
        return None

    return App.Vector(float(coords[0]), float(coords[1]), float(coords[2]))

def write_meta_data(data, tree):
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
