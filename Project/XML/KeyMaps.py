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
Key maps for LandXML elements and the internal dictionary keys
'''
from Project.Support.Const import Const

class KeyMaps(Const):

    _XML_META = {'name': ('ID', '', '', True), 'desc': ('Description', '', '', True),
                 'oID': ('ObjectID', '', '', False), 'state': ('Status', '', '', False)
                }

    _XML_GEO_META = {**_XML_META,
                     **{'length': ('Length', 'float', 0.0, True),
                        'staStart': ('StartStation', 'float', 0.0, True),
                        'note': ('Note', '', '', False)
                       }
                    }

    ALIGNMENT = {
        'Project': {},
        'Application': {'version': ('Version', '', '', False)},
        'CoordGeom' : _XML_META,
        'Alignment': {**_XML_META,
                      **{'length': ('Length', 'float', 0.0, True), 
                         'staStart': ('StartStation', 'float', 0.0, True),
                         'note': ('Note', '', '', False)
                        }
                     }
    }

    META_TAGS = {
        'req': {'length': ('Length', 'float', 0.0), 'staStart': ('StartStation', 'float', 0.0)},
        'opt': {'name': ('ID', '', 'Alignment'), 'desc': ('Description', '', ''),
        'oID': ('ObjectID', '', ''), 'state': ('Status', '', 'proposed')}
    }

    STATION_TAGS = {
        'req': {'staAhead': ('Ahead', 'float', 0.0), 'staInternal': ('Position', 'float', 0.0)},
        'opt': {'staBack': ('Back', 'float', 0.0), 'staIncrement': ('Direction', '', 0.0),
                'desc': ('Description', '', '')}
    }

    GEOM_TAGS = {}
    GEOM_TAGS['Line'] = {
        'req': {},
        'opt': {
            'desc': ('Description', '', ''), 'dir': ('BearingOut', 'float', 'nan'),
            'dir': ('BearingIn', 'float', 'nan'), 'length': ('Length', 'float', 0.0),
            'name': ('Name', '', ''), 'staStart': ('StartStation', 'float', None),
            'state': ('Status', '', ''), 'oID': ('ObjectID', '', ''), 'note': ('Note', '', '')
        }
    }

    GEOM_TAGS['Spiral'] = {
        'req': {
            'length': ('Length', 'float', 0.0), 'radiusEnd': ('RadiusEnd', 'float', 0.0),
            'radiusStart': ('RadiusStart', 'float', 0.0), 'rot': ('Direction', '', 0.0),
            'spiType': ('SpiralType', '', 'clothoid')
        },
        'opt': {
            'chord': ('Chord', 'float', 0.0), 'constant': ('Constant', 'float', 0.0),
            'desc': ('Description', '', ''), 'dirEnd': ('BearingOut', 'float', ''),
            'dirStart': ('BearingIn', 'float', 'nan'), 'external': ('External', 'float', 0.0),
            'length': ('length', 'float', 0.0), 'midOrd': ('MiddleOrdinate', 'float', 0.0),
            'name': ('Name', '', ''), 'radius': ('Radius', 'float', 0.0),
            'staStart': ('StartStation', 'float', None), 'state': ('Status', '', 'proposed'),
            'tangent': ('Tangent', 'float', 0.0), 'oID': ('ObjectID', '', ''), 
            'note': ('Note', '', '')
        }
    }

    LENGTH_TAGS = ['radius', 'radiusStart', 'radiusEnd',
                   'chord', 'external', 'midOrd', 'tangent', 'length']

    ANGLE_TAGS = ['delta', 'dir', 'dirStart', 'dirEnd']

    GEOM_TAGS['Curve'] = {
        'req': {'rot': ('Direction', '', 0.0)},
        'opt': {
            'chord': ('Chord', 'float', 0.0), 'crvType': ('CurveType', '', 'arc'),
            'delta': ('Delta', 'float', 0.0), 'desc': ('Description', '', ''),
            'dirEnd': ('BearingOut', 'float', 'nan'), 'dirStart': ('BearingIn', 'float', 'nan'), 'external': ('External', 'float', 0.0), 'length': ('Length', 'float', 0.0),
            'midOrd': ('MiddleOrdinate', 'float', 0.0), 'name': ('Name', '', ''),
            'radius': ('Radius', 'float', 0.0), 'staStart': ('StartStation', 'float', None),
            'state': ('Status', '', 'proposed'), 'tangent': ('Tangent', 'float', 0.0),
            'oID': ('ObjectID', '', ''), 'note': ('Note', '', '')
        }
    }


    XML_META_KEYS = {'name': 'ID', 'staStart': 'StartStation', 'desc': 'Description', 'state': 'Status', 'length': 'Length', 'units': 'Units'}
    XML_META_TYPES = {'name': 'string', 'staStart': 'float', 'desc': 'string', 'state': 'string', 'length': 'float', 'units': 'string'}
    XML_STATION_KEYS = {'staAhead': 'Ahead', 'staBack': 'Back', 'staInternal': 'Position', 'staIncrement': 'Direction', 'desc': 'Description'}
    XML_STATION_TYPES = {'staAhead': 'float', 'staBack': 'float', 'staInternal': 'float', 'staIncrement': 'int', 'desc': 'string'}
    XML_CURVE_KEYS = {}
    XML_CURVE_KEYS_TYPES = {}
    XML_CURVE_KEYS_OPT = {}
    XML_CURVE_KEYS_OPT_TYPES = {}

    XML_CURVE_KEYS['arc'] = {'rot':'Direction', 'dirStart': 'InBearing', 'dirEnd': 'OutBearing', 'radius': 'Radius'}
    XML_CURVE_KEYS_TYPES['arc'] = {'rot': 'string', 'dirStart': 'float', 'dirEnd': 'float', 'radius': 'float'}
    XML_CURVE_KEYS_OPT['arc'] = {'chord': 'Chord', 'delta': 'Delta', 'external': 'External', 'length': 'Length', 'midOrd': 'MiddleOrd', 'tangent': 'Tangent', 'staStart': 'PcStation'}
    XML_CURVE_KEYS_OPT_TYPES['arc'] = {'chord': 'float', 'delta': 'float', 'external': 'float', 'length': 'float', 'midOrd': 'float', 'tangent': 'float', 'staStart': 'float'}
    XML_CURVE_KEYS['spiral'] = {'rot': 'Direction', 'dirStart': 'InBearing', 'dirEnd': 'OutBearing', 'staStart': 'PcStation', 'radiusStart': 'Radius', 'length': 'Length'}
    XML_CURVE_KEYS_TYPES['spiral'] = {'rot': 'string', 'dirStart': 'float', 'dirEnd': 'float', 'staStart': 'float', 'radius': 'float', 'length': 'float'}
    XML_CURVE_KEYS_OPT['spiral'] = {'chord': 'Chord', 'theta': 'Delta', 'constant': 'Constant', 'desc': 'Description', 'totalX': 'TotalX', 'totalY': 'TotalY', 'tanLong': 'Tangent', 'tanShort': 'InternalTangent'}
    XML_CURVE_KEYS_OPT_TYPES['spiral'] = {'chord': 'float', 'theta': 'float', 'constant': 'float', 'totalX': 'float', 'totalY': 'float', 'tanLong': 'float', 'tanShort': 'float'}

    #A line is simply a curve with zero radius.  It's direction is the out-going bearing, it's PI is the starting point
    XML_LINE_KEYS = {'dir': 'OutBearing','length': 'Length', 'staStart': 'PcStation'}
    XML_LINE_KEYS_TYPES = {'dir': 'float', 'length': 'float', 'staStart': 'float'}
