# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
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

import numpy as np
from scipy import interpolate

import FreeCAD  as App
import FreeCADGui as Gui
import PySide
from PySide import  QtGui, QtCore
import Draft
import Part

def combineCurves():

    #get selected horizontal and vertical geometry
    (hz,vt) = Gui.Selection.getSelection()

    #get list of geometry edges
    hz_edge = hz.Shape.Edges[0]
    vt_edge = vt.Shape.Edges[0]

    #get the horizontal curve's first and last parameters
    first_parm = hz_edge.FirstParameter
    last_parm = hz_edge.LastParameter


    #get the length of the curve and set the step interval
    hz_len = hz_edge.Length

    step = 3000

    #initialize point lists
    #pts = []
    #ptsh = [App.Vector(), App.Vector(hz_len, 0, 0), App.Vector()]
    #ptsn = []
    ptsc = []

    #divide the length by the number of steps, truncating the integer
    #then add one for the concluding point for the steps,
    #plus a point for the end of the edge, if the step point falls short
    point_count = int(hz_len / float(step)) + 1

    if ((point_count - 1) * step) < hz_len:
        point_count += 1

    #vertial curve as equidistant points at the step interval...
    vt_pts = vt_edge.discretize(Number=point_count, First=0.00, Last=hz_len)

    end_point = vt_pts[point_count - 1]

    #this pairs coordinates of like axes in three tuples (x_coords,y_coords,z)
    vt_pt_axes = np.array(vt_pts).swapaxes(0, 1)

    #save the x_coords/y_coords coordinate pairs in separate variables
    x_coords = list(range(0, int(hz_len) + 1, step))

    #if we added two to the point count, then the step interval
    #won't quite make it to the end... add the length as the last point
    if len(x_coords) < point_count:
        x_coords.append(hz_len)

    y_coords = vt_pt_axes[1]

    #append the final elevation - see above
    if (len(y_coords) < point_count):
        y_coords = np.append(y_coords, end_point.y)

    #interpolation...
    ff = interpolate.interp1d(x_coords, y_coords, kind='cubic', bounds_error=False, fill_value=0)

    ll = int(hz.Shape.Length) + 1

    #create a set of x_coords-values evenly spaced between 0 and ll at the specified step interval
    xnew = np.arange(0, ll, step)

    last_element = xnew[len(xnew) - 1]

    if last_element != hz.Shape.Length:
        xnew = np.append(xnew, hz.Shape.Length)

    #interpolates y_coords values for the specified x_coords values
    ynew = ff(xnew)

    for i in range(xnew.shape[0]):

        position = first_parm + step * (last_parm - first_parm) / hz_len * i

        #x,y coordinate on horizontal
        point = hz_edge.Curve.value(position)

        #generate z-coordinate for 3D spline
        ptsc += App.Vector(point.x, point.y, ynew[i])

        #tangent at point
        #tangent = hz_edge.tangentAt(position)

        #stationing line interval
        #f=2
        #if  i%5 == 0:
        #    f=4
        #if  i%10 == 0:
        #    f=10
        #if  i%50 == 0:
        #    f=30

        #calculate normal vector at point
        #n=f*t.cross(FreeCAD.Vector(0,0,1))

        #hp = App.Vector(point.x, point.y, ynew[i])

        #pts += [p,p+n,p,p-n,p]
        #ptsn += [p,hp,p]

        #hh=FreeCAD.Vector(xnew[i],ynew[i],0)
        #vpp = vert_edge.Curve.parameterAtDistance(xnew[i])

        #vtt=vert_edge.tangentAt(vpp)
        #vn=f*vtt.cross(FreeCAD.Vector(0,0,1))

        #ptsh += [hh,hh+vn,hh-vn,hh]

    #stationing along horizontal curve
    #res = App.ActiveDocument.getObject("Wxy")
    #if res == None:
    #    res=App.activeDocument().addObject('Part::Feature','Wxy')

    #res.Shape=Part.makePolygon(pts)

    #
    #res=App.ActiveDocument.getObject("Whmap")
    #if res == None:
    #    res=App.activeDocument().addObject('Part::Feature','Whmap')

    #res.Shape=Part.makePolygon(ptsn)

    #station along vertical curve
    #res=App.ActiveDocument.getObject("Wh")
    #if res == None:
    #    res=App.activeDocument().addObject('Part::Feature','Wh')

    #res.Shape=Part.makePolygon(ptsh)

    #res=App.ActiveDocument.getObject("W3D")
    #if res == None:
    res = App.activeDocument().addObject('Part::Feature','W3D')

    s = Part.BSplineCurve()
    s.interpolate(ptsc)

    res.Shape = s.toShape()
