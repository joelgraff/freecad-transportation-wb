# -*- coding: utf-8 -*-
#************************************************************************
#*                                                                      *
#*   Copyright (c) 2018                                                 *
#*   Joel Graff                                                         *
#*   <monograff76@gmail.com>                                            *
#*                                                                      *
#*  This program is free software; you can redistribute it and/or modify*
#*  it under the terms of the GNU Lesser General Public License (LGPL)  *
#*  as published by the Free Software Foundation; either version 2 of   *
#*  the License, or (at your option) any later version.                 *
#*  for detail see the LICENCE text file.                               *
#*                                                                      *
#*  This program is distributed in the hope that it will be useful,     *
#*  but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#*  GNU Library General Public License for more details.                *
#*                                                                      *
#*  You should have received a copy of the GNU Library General Public   *
#*  License along with this program; if not, write to the Free Software *
#*  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#*  USA                                                                 *
#*                                                                      *
#************************************************************************

"""
SketchManager module based on nurbswb/sketchmanager.py from microelly2
"""

__title__ = "SketchManger.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import FreeCADGui as Gui

import Sketcher

def copy_sketch(sketch, target_name):
    '''
    kopiert sketch in sketchobjectpython
    '''
    doc = App.ActiveDocument

    target = doc.addObject('Sketcher::SketchObjectPython', target_name)	

    #_ViewProvider(target.ViewObject)

    for geo in sketch.Geometry:
        index=target.addGeometry(geo)
        target.setConstruction(index, geo.Construction)

    for constraint in sketch.Constraints:
        target.addConstraint(constraint)

    target.Placement = sketch.Placement

    target.solve()
    target.recompute()
    doc.recompute()

    return target

def load_sketch(lib_path, source_name='Sketch', target_name=None):
    '''
    load sketch from file into sketcher object with name.
    Repalces existing sketch if it exists.
    '''

    doc = App.ActiveDocument
    library = App.open(lib_path)

    App.setActiveDocument(doc.Name)

    source = library.getObjectsByLabel(source_name)[0]

    if source is None:
        print("Cannot find library sketch " + source_name)
        return

    if target_name is None:
        target_name = source_name

    sketch = copy_sketch(source, target_name)

    sketch.Label = "Copy of " + source_name + "@" + lib_path

    App.closeDocument(library.Label)

    return sketch
