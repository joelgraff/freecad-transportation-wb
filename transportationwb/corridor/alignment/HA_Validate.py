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
Validation for horizontal alignment data ensuring correct order
and complete descriptions
'''
import math

import FreeCAD as App
import FreeCADGui as Gui
import Draft
import numpy

from transportationwb.ScriptedObjectSupport import Properties, Units, Utils, DocumentProperties
from transportationwb.XML.HorizontalKeyMaps import HorizontalKeyMaps

def metadata(data):
    '''
    Return valid metadata
    '''

    return data

def station_equations(data):
    '''
    Return valid station equation data
    '''

    if data is None:
        return [obj.Station_Equations.append(]App.Vector(0.0, 0.0, 0.0)]

    result = []

    for key in data.keys():

        back = key[0]
        ahead = key[1]

        eqns.append(App.Vector(back, ahead, 0.0))

    return result

def _validate_curve(data):
    '''
    Validate a curve
    '''

    for key in HorizontalKeyMaps().XML_CURVE_KEYS_OPT.keys():

        if key in data.keys():
            continue

        if key == ''

def geometry_data(data):
    '''
    Validate the coordinate geometry data by ensuring
    PI data is continuous within the alignment and ordering the
    internal data set accordingly.
    data - a list of curve dictionaries
    '''

    matches = []

    curve_data = data['curve']
    data_len = len(curve_data)

    for _i in range(0, data_len):
        
        ################# Test for coincident endpoints
        curve_1 = curve_data[_i]
        end_point = curve_1.get('End')

        if end_point:

            #test for coincident start / end points
            for _j in range(0, data_len):

                start_point = curve_data[_j].get('Start')

                if start_point:

                    #arbitrary tolerance check to determine if points are close enough to be merged
                    if end_point.distanceToPoint(start_point) < 1.0:
                        matches.append([_i, _j])
                        break

            #skip the rest if a match was found
            if matches[-1][0] == _i:
                continue

        ############## Test for identical bearings
        out_bearing = curve_1.get('OutBearing')

        if out_bearing:

            lst = []

            for _j in range(0, data_len):

                #matching bearings may be adjacent curves
                if out_bearing == curve_data[_j].get('InBearing'):
                    lst.append(_j)

            #no matches found, skip the remainder of the iteration
            if not lst:
                continue

            #one match found, save it and move on
            if len(lst) == 1:
                matches.append([_i, lst[0]])
                continue

            #still here?  Multiple matches found.
            #test for more than one curve with a matching bearing,
            #picking the shortest as the adjacent curve
            max_dist = None
            nearest_pi = None

            for _x in lst:

                pi_1 = curve_1.get('PI')
                pi_2 = curve_data[_j].get('PI')

                if not pi_1 or not pi_2:
                    print ('Missing PI in ' + self.Object.ID)
                    return None

                if pi_1 != pi_2:

                    dist = pi_1.distanceToPoint(pi_2)

                    if max_dist:
                        if dist < max_dist:
                            max_dist = dist
                            nearest_pi = _j

            if nearest_pi:
                matches.append([_i, nearest_pi])

    if len(matches) != data_len - 1:
        print('%d curves found, %d unmatched' % (data_len, data_len - len(matches) - 1))
        print('Alignment ', self.Object.ID, ' is discontinuous.')
        return None

    ordered_list = matches
    old_len = len(ordered_list) + 1

    while len(ordered_list) < old_len:
        old_len = len(ordered_list)
        ordered_list = self._order_list(ordered_list)

    self.geometry = curve_data

    #with an ordered list of indices, create a new data set in the correct order
    if ordered_list[0] != list(range(0, data_len)):
        self.geometry = [curve_data[_i] for _i in ordered_list[0]]

    

def _order_list(self, tuples):
    '''
    Combine a list of tuples where endpoints of two tuples match
    '''

    if len(tuples) == 1:
        return tuples

    tuple_end = len(tuples[0]) - 1
    tuple_count = len(tuples)
    tuple_pairs = []

    for _i in range(0, tuple_count):

        _tpl1 = tuples[_i]

        for _tpl2 in tuples[(_i + 1):]:

            ordered_tuple = None

            if _tpl1[0] == _tpl2[tuple_end]:
                ordered_tuple = _tpl2
                ordered_tuple.extend(_tpl1[1:])

            elif _tpl1[tuple_end] == _tpl2[0]:
                ordered_tuple = _tpl1 
                ordered_tuple.extend(_tpl2[1:])

            if ordered_tuple:
                tuple_pairs.append(ordered_tuple)

    return tuple_pairs

def _get_station_position(self, station):
    '''
    Using the station equations, determine the position along the alingment
    '''

    start_sta = self.Object.Station_Equations[0].y

    eqs = self.Object.Station_Equations

    #shortcut if only the starting station is specified
    if len(eqs) == 1:
        return station - start_sta

    position = 0.0

    for _eq in eqs[1:]:

        #return the internal position if the station falls within the equation
        if start_sta < station < _eq.x:
            return position + station - start_sta

        #increment the position by the equaion length and
        #set the starting station to the next equation
        position += _eq.x - start_sta
        start_sta = _eq.y

    #no more equations - station falls outside of last equation
    return position + station - start_sta

def set_data(self, data):
    '''
    Assign curve data to object, parsing and converting to coordinate form
    '''

    self.no_execute = True

    self.assign_meta_data(data['meta'])
    self.assign_station_data(data['station'])

    #int_eq = self.Object.Intersection_Equation

    #if int_eq.Length:
    #    datum = self._get_coordinate_at_station(int_eq[0], self.Object.Parent_Alignment) / 304.80

    self.assign_geometry_data(data)

    delattr(self, 'no_execute')

    self.Object.Points = self._discretize_geometry()

    #update the document data FPO with the new alignment dataset
    if not self.xml_fpo:
        self.xml_fpo = XmlFpo.create()

    self.xml_fpo.update('alignment', self.ID, self.data)            
