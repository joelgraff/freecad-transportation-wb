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

from xml.etree import ElementTree as etree

import FreeCAD as App

from transportationwb.ScriptedObjectSupport import Units, LandXml, Utils

class AlignmentImporter(object):
    '''
    LandXML parsing class for alignments
    '''

    #LandXML attribute tags and corresponding data types - empty type defaults to 'string'
    #'name' is required, but is tested for explictly, so it is considered optional here
    META_TAGS = {
        'req': {'length': ('Length', 'float'), 'staStart': ('StartStaion', 'float')},
        'opt': {'name': ('ID', ''), 'desc': ('Description', ''), 'oID': ('ObjectID', ''),
                'state': ('Status', '')}
    }

    STATION_TAGS = {
        'req': {'staAhead': ('Ahead', 'float'), 'staInternal': ('Position', 'float')},
        'opt': {    'staBack': ('Back', 'float'), 'staIncrement': ('Direction', ''),
                    'desc': ('Description', '')}
    }

    GEOM_TAGS = {}
    GEOM_TAGS['line'] = {
        'req': {},
        'opt': {
            'desc': ('Description', ''), 'dir': ('BearingOut', 'float'),
            'length': ('Length', 'float'), 'name': ('Name', ''),
            'staStart': ('StartStation', 'float'), 'state': ('Status', ''),
            'oID': ('ObjectID', ''), 'note': ('Note', '')
        }
    }

    GEOM_TAGS['spiral'] = {
        'req': {
            'length': ('Length', 'float'), 'radiusEnd': ('RadiusEnd',  'float'),
            'radiusStart': ('RadiusStart', 'float'), 'rot': ('Direction', ''),
            'spiType': ('SpiralType', '')
        },
        'opt': {
            'chord': ('Chord', 'float'), 'constant': ('Constant', 'float'),
            'desc': ('Description', ''), 'dirEnd': ('OutBearing', 'float'),
            'dirStart': ('InBearing', 'float'), 'external': ('External', 'float'),
            'length': ('length', 'float'), 'midOrd': ('MiddleOrdinate', 'float'),
            'name': ('Name', ''), 'radius': ('Radius', 'float'),
            'staStart': ('StartStation', 'float'), 'state': ('Status', ''),
            'tangent': ('Tangent', 'float'), 'oID': ('ObjectID', ''), 'note': ('Note', '')
        }
    }


    GEOM_TAGS['arc'] = {
        'req': {'rot': ('Direction', '')},
        'opt': {
            'chord': ('Chord', 'float'), 'crvType': ('CurveType', ''), 'delta': ('Delta', 'float'),
            'desc': ('Description', ''), 'dirEnd': ('OutBearing', 'float'),
            'dirStart': ('InBearing', 'float'), 'external': ('External', 'float'),
            'length': ('length', 'float'), 'midOrd': ('MiddleOrdinate', 'float'),
            'name': ('Name', ''), 'radius': ('Radius', 'float'),
            'staStart': ('StartStation', 'float'), 'state': ('Status', ''),
            'tangent': ('Tangent', 'float'), 'oID': ('ObjectID', ''), 'note': ('Note', '')
        }
    }


    def __init__(self):

        self.errors = []

    def _validate_units(self, units):
        '''
        Validate the units of the alignment, ensuring it matches the document
        '''

        if units is None:
            print('Missing units')
            return ''

        xml_units = units[0].attrib['linearUnit']

        if xml_units != Units.get_doc_units()[1]:
            self.errors.append(
                'Document units of ' + Units.get_doc_units()[1] + ' expected, units of ' +
                xml_units + 'found')
            return ''

        return xml_units

    @staticmethod
    def _convert_token(value, typ):
        '''
        Converts a string token to a float or integer value as indicated by type
        Returns None if fails
        value = string token
        typ = numeric type: 'float', 'int', 'vector'
        '''

        if not value:
            return None

        if typ == 'string' or not typ:
            return value

        if typ == 'int':
            return Utils.to_int(value)

        if typ == 'float':
            return Utils.to_float(value)

        if typ == 'vector':
            coords = Utils.to_float(value.split(' '))

            if coords:
                return App.vector(coords)

        return None

    @staticmethod
    def _get_alignment_name(alignment, alignment_keys):
        '''
        Return a valid alignment name, if not defiend or otherwise duplicate
        '''

        align_name = alignment.attrib.get('name')

        #alignment name is requiredand must be unique
        if align_name is None:
            align_name = 'Unkown Alignment '

        counter = 0

        #test for key uniqueness
        while align_name + str(counter) in alignment_keys:
            counter += 1

        if counter:
            align_name += str(counter)

        return align_name

    def _parse_data(self, align_name, tags, attrib):
        '''
        '''
        result = {}

        #test to ensure all required tags are in the imrpoted XML data
        missing_tags = set(
            list(tags['req'].keys())
        ).difference(
            set(list(attrib.keys()))
        )

        #report error and skip the alignment if required tags are missing
        if missing_tags:
            self.errors.append(
                'The required XML tags were not found in alignment %s:\n%s'
                % (align_name, missing_tags)
            )
            return None

        #merge the required / optional tag dictionaries and iterate the items
        for key, _tuple in  {**tags['req'], **tags['opt']}.items():

            attr_val = self._convert_token(attrib.get(key), _tuple[1])

            if attr_val is None:

                if key in tags['req']:
                    self.errors.append(
                        'Missing or invalid %s attribute in alignment %s'
                        % (_tuple[0], align_name)
                    )

            result[_tuple[0]] = attr_val

        return result

    def _parse_meta_data(self, align_name, alignment):
        '''
        Parse the alignment elements and strip out meta data for each alignment,
        returning it as a dictionary keyed to the alignment name
        '''

        return self._parse_data(align_name, self.META_TAGS, alignment.attrib)

    def _parse_station_data(self, align_name, alignment):
        '''
        Parse the alignment data to get station equations and return a list of equation dictionaries
        '''

        result = []

        equations = LandXml.get_children(alignment, 'StaEquation')

        for equation in equations:
            result.append(self._parse_data(align_name, self.STATION_TAGS, equation.attrib))

        return result

    def _parse_geo_data(self, align_name, geometry, curve_type):
        '''
        Parse curve data and return as a dictionary
        '''

        result = []
        _geom_tags = self.GEOM_TAGS[curve_type]

        for curve in geometry:

            #add the curve / line start / center / end coordinates, skipping if any are missing
            _start = Utils.to_float(LandXml.get_child(curve, 'Start'))
            _center = Utils.to_float(LandXml.get_child(curve, 'Center'))
            _end = Utils.to_float(LandXml.get_child(curve, 'End'))
            _pi = Utils.to_float(LandXml.get_child(curve, 'PI'))

            if curve_type == 'line' and not (_start and _end):
                self.errors.append(
                    'Missing %s points in alignment %s'
                    % (curve_type, align_name)
                )

            elif not (_start and _center and _end):
                self.errors.append(
                    'Missing %s points in alignment %s'
                    % (curve_type, align_name)
                )

            coords = {'Type': curve_type, 'Start': _start, 'Center': _center, 'End': _end, 
                      'PI': _pi}

            result.append({
                **coords,
                **self._parse_data(align_name, self.GEOM_TAGS[curve_type], curve.attrib)
            })

        return result

    def _parse_coord_geo_data(self, align_name, alignment):
        '''
        Parse the alignment coorinate geometry data to get curve information and
        return as a dictionary
        '''

        coord_geo = LandXml.get_child(alignment, 'CoordGeom')

        if not coord_geo:
            print('Missing coordinate geometry for ', align_name)
            return None

        result = {}

        curves = LandXml.get_children(coord_geo, 'Curve')
        spirals = LandXml.get_children(coord_geo, 'Spiral')
        lines = LandXml.get_children(coord_geo, 'Line')

        result['arc'] = self._parse_geo_data(align_name, curves, 'arc')
        result['spiral'] = self._parse_geo_data(align_name, spirals, 'spiral')
        result['line'] = self._parse_geo_data(align_name, lines, 'line')

        #spirals, 2-center, 3-center, superelevation...

        return result

    def import_file(self, filepath):
        '''
        Import a LandXML and build the Python dictionary fronm the appropriate elements
        '''

        #get element tree and key nodes for parsing
        doc = etree.parse(filepath)
        root = doc.getroot()

        project = LandXml.get_child(root, 'Project')
        units = LandXml.get_child(root, 'Units')
        alignments = LandXml.get_child(root, 'Alignments')

        #aport if key nodes are missing
        if not units:
            self.errors.append('Missing project units')
            return None

        unit_name = self._validate_units(units)

        if not unit_name:
            self.errors.append('Invalid project units')
            return None

        #default project name if missing
        project_name = 'Unknown Project'

        if not project is None:
            project_name = project.attrib['name']

        #build final dictionary and return
        result = {}
        result['Project'] = {}
        result['Project'][self.META_TAGS['opt']['name'][0]] = project_name
        result['Alignments'] = {}

        for alignment in alignments:

            align_name = self._get_alignment_name(alignment, list(result.keys()))

            result['Alignments'][align_name] = {}
            align_dict = result['Alignments'][align_name]

            align_dict['meta'] = self._parse_meta_data(align_name, alignment)
            align_dict['station'] = self._parse_station_data(align_name, alignment)
            align_dict['geometry'] = self._parse_coord_geo_data(align_name, alignment)

        return result
