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
Alignment Feature Python object which wraps geometry that provides alignments for transportation facilities and structures
"""
__title__ = "alignment.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import BoxCulvert
import FreeCAD as App
import FreeCAD as Gui

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def create_1_cell_box():
    """
    Creates single-cell box, and extrudes it along the selected alignment object
    """

    #add a group for the box culvert structure
    obj = App.ActiveDocument.addObject("App::FeaturePython", "BoxCulvert1Cell")

    obj.Label = translate("Transportation", "BoxCulvert1Cell")

    #create the box culvert object
    box = BoxCulvert.BoxCulvert(obj)

    lib_path = App.ConfigGet("UserAppData") + "Mod\\freecad-transportation-wb\\data\\drainage\\box_culvert1.FCStd"

    #get and validate the selected sweep path
    sel = Gui.Selection.getSelection()[0]
    valid_sel = None

    if hasattr(sel, "Proxy"):
        if hasattr(sel.Proxy, "Type"):
            if sel.Proxy.Type == "Alignment"
                valid_sel = sel

    if valid_sel is None:
        print ("Invalid selection for sweep")
        return None

    box.SweepPath = valid_sel

    #reference the sketch to sweep and orient it along the path
    box.attach_sketch(lib_path, "box_1_cell")
    box.set_sketch_normal()
    
    App.ActiveDocument.recompute()

    #sweep the profile
    box.sweep_sketch(10000.0)

    return obj

def draft_ends():
    
    sel = Gui.Selection.getSelection()

    face_count = 0

    if len(sel) == 2:
        for i in range(2):
            if hasattr(sel[i], "ShapeType"):
                if sel[i].ShapeType == 'Face'
                    face_count += 1

    if face_count != 2:
        print ("invalid selection")
        return None

    doc = App.ActiveDocument
    
    Gui.ActiveDocument.setActiveObject('pdbody', None)
    Gui.ActiveView.setActiveObject('pdbody', doc.findObjects('PartDesign::Body')[0])

    doc.Draft.Base = (doc.)
>>> App.activeDocument().Draft.Base = (App.ActiveDocument.box_1_cell_Sweep,["Face1"])
>>> Gui.Selection.clearSelection()
>>> Gui.activeDocument().hide("box_1_cell_Sweep")
>>> App.ActiveDocument.recompute()
>>> Gui.activeDocument().setEdit('Draft', 0)
>>> Gui.Selection.clearSelection()
>>> Gui.ActiveDocument.Draft.ShapeColor=Gui.ActiveDocument.box_1_cell_Body.ShapeColor
>>> Gui.ActiveDocument.Draft.LineColor=Gui.ActiveDocument.box_1_cell_Body.LineColor
>>> Gui.ActiveDocument.Draft.PointColor=Gui.ActiveDocument.box_1_cell_Body.PointColor
>>> Gui.ActiveDocument.Draft.Transparency=Gui.ActiveDocument.box_1_cell_Body.Transparency
>>> Gui.ActiveDocument.Draft.DisplayMode=Gui.ActiveDocument.box_1_cell_Body.DisplayMode