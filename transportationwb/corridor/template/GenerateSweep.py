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

def regenerate(loft, section_shape):
    '''
    Regenerate the loft with a new section
    '''


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

    @staticmethod
    def _build_sections(spline_path, section_sketch):

        #reference spline curve object
        curve = spline_path.Curve

        #return first / last parameters?
        [a,b]=spline_path.ParameterRange

        #round the length up and add one
        bm=int(round(b))+1

        #reference to the shape objecct
        #ff=App.ActiveDocument.Template.Shape

        #list initialization
        comps = []

        #Z-up vector
        z_up = App.Vector(0, 0, 1)

        #iterate the range of the length as integers
        i = 0.0
        step = 304.8 * 1

        sketch_points = []

        for vtx in section_sketch.Shape.Vertexes:
            sketch_points.append(vtx.Point)

        while i < bm:

            normal = curve.tangent(i)[0].cross(z_up).normalize()

            #get the coordinate of the sweep path at the first millimeter
            origin = curve.value(i)

            #get the tangent of the sweep path at that coordinate
            tangent = curve.tangent(i)

            #calculate the normal against z-up and normalize
            x_normal = tangent[0].cross(z_up).normalize()
            z_normal = tangent[0].cross(x_normal).normalize()

            #z-coordinate should always be positive
            if z_normal.z < 0.0:
                z_normal = z_normal.negative()

            poly_points = []

            for point in sketch_points:
                poly_points.append(origin + (point.x * normal) + (point.y * z_normal))

            poly_points.append(origin)

            #generate a polygon of the points and save it
            comps += [Part.makePolygon(poly_points)]

            i += step

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

        section_list = self._build_sections(Gui.Selection.getSelection()[0].Shape.Edges[0], Gui.Selection.getSelection()[1])

        #create a compound of the components (polygons)
        sections = parent.newObject('Part::Feature', sweep_name + '_sections')
        sections.Shape = Part.Compound(section_list)

        #loft the polygons to generate the solid
        loft = parent.newObject('Part::Feature', 'loft')
        loft.Shape = Part.makeLoft(section_list, False, True, False)

Gui.addCommand('GenerateSweep', GenerateSweep())