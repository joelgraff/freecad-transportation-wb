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

    #find the parent body object
    body = gui_sel.getSelection()[0].getParentGeoFeatureGroup()
    sweep = None

    if body.TypeId != 'PartDesign::Body':
        print("invalid object heirarchy.  Body not found.")
        return None

    #get the additive pipe sweep object
    for child in body.Group:
        if child.TypeId == "PartDesign::AdditivePipe":
            sweep = child
            break

    if sweep is None:
        print("Sweep object not found.")
        return None

    #get the parameter object
    grp = body.getParentGroup().Group
    parameters = None

    for child in  grp:
        if "Parameters" in child.Label:
            parameters = child

    if parameters is None:
        print("Unable to find Parameters object")
        return None        

    #perform draft
    draft_object = body.newObject("PartDesign::Draft", "Draft_" + faces[0])
    draft_object.Base = (sweep, [faces[0]])
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

    draft_object.setExpression("Angle", parameters.Label + ".Skew")
    draft_object.Reversed = 0
    draft_object.NeutralPlane = (sweep, [faces[1]])
    draft_object.PullDirection = None
    draft_object.Base = (sweep, [faces[0]])

    app_doc.recompute()
