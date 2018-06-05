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

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def create_1_cell_box():
    """
    Creates single-cell box, and extrudes it along the selected alignment object
    """

    #add a group for the box culvert structure
    obj = App.ActiveDocument.addObject("App::DocumentObjectGroupPython", "BoxCulvert1Cell")

    obj.Label = translate("Transportation", "BoxCulvert1Cell")

    #create the box culvert object
    box = BoxCulvert.BoxCulvert(obj)

    lib_path = App.ConfigGet("UserAppData") + "Mod\\freecad-transportation-wb\\data\\drainage\\box_culvert1.FCStd"

    #get and validate the selected sweep path
    sel = Gui.Selection.getSelection()
    valid_sel = None

    #abort if no selection
    if not sel:
        print("No alignment selected")
        return None

    if hasattr(sel[0], "Proxy"):
        if hasattr(sel[0].Proxy, "Type"):
            if sel[0].Proxy.Type == "Alignment":
                valid_sel = sel[0].Group[0]

    if valid_sel is None:
        print ("Invalid selection for sweep")
        return None

    box.SweepPath = valid_sel

    #reference the sketch to sweep and orient it along the path
    box.attach_sketch(lib_path, "box_1_cell")
    box.orient_profile()

    App.ActiveDocument.recompute()

    #sweep the profile
    box.sweep_sketch(10000.0)

    return obj

def draft_ends():
    
    app_doc = App.ActiveDocument
    gui_doc = Gui.ActiveDocument
    gui_sel = Gui.Selection
    faces = gui_sel.getSelectionEx()[0].SubElementNames
    face_count = 0

    #ensurce exactly two objects are selected
    #and count the number of faces
    if len(faces) == 2:
        for i in range(2):
            if "Face" in faces[i]:
                face_count += 1

    #fail if both objects are not faces
    if face_count != 2:
        print ("invalid face selection")
        return None

    sel = gui_sel.getSelection()

    #ensure selected faces are both on the same object
    if sel[0].Name != sel[1].Name:
        print ("Selected faces must share the same object")
        return None

    add_pipe = gui_sel.getSelection()[0]
    body = None

    #type-check the objects in the hierarchy
    if add_pipe.TypeId == "PartDesign::AdditivePipe":
        body = add_pipe.getParentGeoFeatureGroup()

        if body.TypeId == "PartDesign::Body":
            Gui.activeView().setActiveObject('pdbody', body)

    if body is None:
        print ("invalid object heirarchy.  Additive Pipe or Body not found.")
        return None

    
    #perform draft
    draft_object = body.newObject("PartDesign::Draft", "Draft_" + faces[0])
    draft_object.Base = (add_pipe, [faces[0]])
    gui_sel.clearSelection()

    app_doc.recompute()

    #Gui.activeDocument().setEdit('Draft', 0)
    gui_draft = gui_doc.getObject(draft_object.Name)
    gui_body = gui_doc.getObject(body.Name)

    gui_draft.ShapeColor = gui_body.ShapeColor
    gui_draft.LineColor = gui_body.LineColor
    gui_draft.PointColor = gui_body.PointColor
    gui_draft.Transparency = gui_body.Transparency
    gui_draft.DisplayMode = gui_body.DisplayMode

    draft_object.Angle = 30.0
    draft_object.Reversed = 0
    draft_object.NeutralPlane = (add_pipe, [faces[1]])
    draft_object.PullDirection = None
    draft_object.Base = (add_pipe, [faces[0]])

    app_doc.recompute()
    

#-----------------------------------------------------------------
#>>> App.activeDocument().box_1_cell001_Body.newObject("PartDesign::Draft","Draft")
#>>> App.activeDocument().Draft.Base = (App.ActiveDocument.box_1_cell001_Sweep,["Face1"])
#>>> Gui.Selection.clearSelection()
#>>> Gui.activeDocument().hide("box_1_cell001_Sweep")
#>>> App.ActiveDocument.recompute()
#>>> Gui.activeDocument().setEdit('Draft', 0)
#>>> Gui.Selection.clearSelection()
#>>> Gui.ActiveDocument.Draft.ShapeColor=Gui.ActiveDocument.box_1_cell001_Body.ShapeColor
#>>> Gui.ActiveDocument.Draft.LineColor=Gui.ActiveDocument.box_1_cell001_Body.LineColor
#>>> Gui.ActiveDocument.Draft.PointColor=Gui.ActiveDocument.box_1_cell001_Body.PointColor
#>>> Gui.ActiveDocument.Draft.Transparency=Gui.ActiveDocument.box_1_cell001_Body.Transparency
#>>> Gui.ActiveDocument.Draft.DisplayMode=Gui.ActiveDocument.box_1_cell001_Body.DisplayMode
#>>> App.ActiveDocument.Draft.Angle = 45.000000
#>>> App.ActiveDocument.Draft.Reversed = 0
#>>> App.ActiveDocument.Draft.NeutralPlane = (App.ActiveDocument.box_1_cell001_Sweep, ["Face8"])
#>>> App.ActiveDocument.Draft.PullDirection = None
#>>> App.ActiveDocument.Draft.Base = (App.ActiveDocument.box_1_cell001_Sweep,["Face1",])
#>>> Gui.activeDocument().hide("box_1_cell001_Sweep")
#>>> App.ActiveDocument.recompute()
#>>> Gui.activeDocument().resetEdit()


#>>> App.activeDocument().box_1_cell001_Body.newObject("PartDesign::Draft","Draft001")
#>>> App.activeDocument().Draft001.Base = (App.ActiveDocument.Draft,["Face3"])
#>>> Gui.Selection.clearSelection()
#>>> Gui.activeDocument().hide("Draft")
#>>> App.ActiveDocument.recompute()
#>>> Gui.activeDocument().setEdit('Draft001', 0)
#>>> Gui.Selection.clearSelection()
#>>> Gui.ActiveDocument.Draft001.ShapeColor=Gui.ActiveDocument.box_1_cell001_Body.ShapeColor
#>>> Gui.ActiveDocument.Draft001.LineColor=Gui.ActiveDocument.box_1_cell001_Body.LineColor
#>>> Gui.ActiveDocument.Draft001.PointColor=Gui.ActiveDocument.box_1_cell001_Body.PointColor
#>>> Gui.ActiveDocument.Draft001.Transparency=Gui.ActiveDocument.box_1_cell001_Body.Transparency
#>>> Gui.ActiveDocument.Draft001.DisplayMode=Gui.ActiveDocument.box_1_cell001_Body.DisplayMode
#>>> App.ActiveDocument.Draft001.Angle = 45.000000
#>>> App.ActiveDocument.Draft001.Reversed = 0
#>>> App.ActiveDocument.Draft001.NeutralPlane = (App.ActiveDocument.Draft, ["Face8"])
#>>> App.ActiveDocument.Draft001.PullDirection = None
#>>> App.ActiveDocument.Draft001.Base = (App.ActiveDocument.Draft,["Face3",])
#>>> Gui.activeDocument().hide("Draft")
#>>> App.ActiveDocument.recompute()
#>>> Gui.activeDocument().resetEdit()