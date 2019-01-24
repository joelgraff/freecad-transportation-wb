# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
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
AddProperty helper function for FeaturePythonObjects
'''

__title__ = "AddProeprty.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App

def add_property(obj, p_type, name, desc, default_value=None, isReadOnly=False, isHidden=False):

    '''
    Build FPO properties

    p_type  The property type, either formal ('App::PropertyFloat') or shortended ('Float')
    name    The Property name as "GROUP.NAME"  If group is omitted, the default is 'Base'
    desc    Tooltip description string
    default_value   Default property value
    isReadOnly      Boolean property (read-only = True)
    '''

    target = obj

    tple = name.split('.')

    p_name = tple[0]
    p_group = 'Base'

    if len(tple) == 2:
        p_name = tple[1]
        p_group = tple[0]


    if p_type in [
            'Length',
            'Distance',
            'Percent',
            'Angle',
            'Link',
            'LinkList',
            'Float',
            'FloatList',
            'Bool',
            'String',
            'StringList'
        ]:
        p_type = 'App::Property' + p_type

    else:
        print('Invalid property type specified: ', p_type)
        return None

    target.addProperty(p_type, p_name, p_group, desc)

    App.ActiveDocument.recompute()

    prop = target.getPropertyByName(p_name)

    if p_type in [
            'App::PropertyFloat'
        ]:
        prop = default_value

    elif p_type in [
            'App::PropertyBool',
            'App::PropertyPercent',
            'App::PropertyLinkList',
            'App::PropertyLink',
            'App::PropertyString',
            'App::PropertyStringList'
        ]:
        setattr(target, p_name, default_value)
        #prop = default_value
    else:
        prop.Value = default_value

    editor_mode = 0

    if isReadOnly:
        editor_mode += 1

    if isHidden:
        editor_mode += 2

    target.setEditorMode(p_name, editor_mode)

    return prop
