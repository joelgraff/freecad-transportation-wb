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
Module to manage document properties for the transportation workbench
'''

__title__ = "DocumentProperties.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App

class DocumentProperty:

    Param = App.ParamGet('User parameter:BaseApp/Preferences/Mod/Transportation')

    @staticmethod
    def _set_string(key, value):
        DocumentProperty.Param.SetString(key, value)

    @staticmethod
    def _get_string(key):
        return DocumentProperty.Param.GetString(key)

    @staticmethod
    def _set_int(key, value):
        DocumentProperty.Param.SetInt(key, value)

    @staticmethod
    def _get_int(key):
        return DocumentProperty.Param.GetInt(key)

    @staticmethod
    def _set_float(key, value):
        DocumentProperty.Param.SetFloat(key, value)
        
    @staticmethod
    def _get_float(key):
        return DocumentProperty.Param.GetFloat(key)

class TemplateLibraryPath():

    @staticmethod
    def get_value():
        return DocumentProperty._get_string('TemplateLibPath')

    @staticmethod
    def set_value(value):
        DocumentProperty._set_string('TemplateLibPath', value)

class MinimumTangentLength(DocumentProperty):

    @staticmethod
    def get_value():
        return DocumentProperty._get_float('MinimumTangentLength')

    @staticmethod
    def set_value(value):
        DocumentProperty._set_float('MinimumTangentLength', value)
