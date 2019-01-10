# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 microelly, Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  Based on original implementation by microelly.  See stationing.py     *
# *  for original implementation.                                          *
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

import Draft
import Part
import os
import time
import FreeCAD as App
import FreeCADGui as Gui

class GenerateSweep():
    '''
    Sweep generation class.
    Builds a sweep based on passed template and sweep path
    '''
    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Ctrl+Alt+G",
                'MenuText': "Generate Sweep",
                'ToolTip' : "Generate sweep of template along a path",
                'CmdType' : "ForEdit"}

    def _build_sections(self):
        #get spline path
        s=Gui.Selection.getSelection()[0].Shape.Edges[0]

        #refernce spline curve object
        c=s.Curve

        #return first / last parameters?
        [a,b]=s.ParameterRange

        #round the length up and add one
        bm=int(round(b))+1

        #reference to the shape objecct
        #ff=App.ActiveDocument.Template.Shape

        #list initialization
        comps = []

        #Z-up vector
        h = App.Vector(0, 0, 1)

        #iterate the range of the length as integers
        i = 0.0
        step = 304.8 * 25
        poly_count = 0

        while i < bm:

            #get the coordinate of the sweep path at the first millimeter
            v = c.value(i)

            #get the tangent of the sweep path at that coordinate
            t = c.tangent(i)

            #calculate the normal against z-up and normalize
            n = t[0].cross(h).normalize()

            #accumulate the sweep path point list with a list of:
            # - the coordinate
            # - the coordinate plus twice the tangent
            # - the coordinate
            # - the coordinate plus twice the normal
            # - the coordinate

            #pts += [v,v+t[0]*2,v,v+n*2,v]

            #create a copy of the shape
            #ff2=ff.copy()

            #reference it's placement and base
            #pm=ff2.Placement
            #v0=pm.Base

            #reference the global placement and base
            #pm2=App.Placement()
           # pm2.Base=v

            #create a list of points containing:
            # - the point,
            # - the point plus twice the normal
            # - the point plus twice the normal plus the unit up vector
            # - the point plus the unit up vector
            # - the point
            ptsa = [v, v+3000*n, v+3000*n+h*200, v+h*200, v]

            #generate a polygon of the points and save it
            ff2 = Part.makePolygon(ptsa)

            #add the polygon to the components list
            comps += [ff2]

            #500 = 76s
            #1000 = 73.6s
            #1500 = 72.6s
            #2000 = 72.9s
            #4000 = 72.0s
            #8000 = 71.0s
            #16000 = 61.0s

            #if poly_count == 500 * 64:
                #result.append(comps)
                #comps = [ff2]
                #poly_count = 0

            i += step
            poly_count = poly_count + 1

        print ('generated ', bm / step, 'polys')

        return comps

    def _validate_tree(self):
        '''
        Validate the current tree structure, ensuring Sweep document group exists
        and return the Sweeps group object

        TODO:  Add popup to select target folder in sweep group and return the target group
        '''

        parent = App.ActiveDocument.findObjects('App::DocumentObjectGroup', 'Sweeps')
        result = None

        if parent == []:
            result = App.ActiveDocument.addObject('App::DocumentObjectGroup', 'Sweeps')
            App.ActiveDocument.recompute()
        else:
            result = parent[0]

        return result

    def Activated(self):

        parent = self._validate_tree()

        sweep_name = 'sweep'
        parent = parent.newObject('App::DocumentObjectGroup', sweep_name)

        section_list = self._build_sections()

        #create a compound of the components (polygons)
        sections = parent.newObject('Part::Feature', sweep_name + '_sections')
        sections.Shape = Part.Compound(section_list)

        #loft the polygons to generate the solid
        loft = parent.newObject('Part::Feature', 'loft')
        loft.Shape = Part.makeLoft(section_list, False, True, False)

Gui.addCommand('GenerateSweep', GenerateSweep())