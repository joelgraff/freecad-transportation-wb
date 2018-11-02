# -*- coding: utf-8 -*-
/**************************************************************************
 *                                                                        *
 *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
 *                                                                        *
 *  This program is free software; you can redistribute it and/or modify  *
 *  it under the terms of the GNU Lesser General Public License (LGPL)    *
 *  as published by the Free Software Foundation; either version 2 of     *
 *  the License, or (at your option) any later version.                   *
 *  for detail see the LICENCE text file.                                 *
 *                                                                        *
 *  This program is distributed in the hope that it will be useful,       *
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *  GNU Library General Public License for more details.                  *
 *                                                                        *
 *  You should have received a copy of the GNU Library General Public     *
 *  License along with this program; if not, write to the Free Software   *
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
 *  USA                                                                   *
 *                                                                        *
 **************************************************************************/

"""
 EndWall - Feature Python object which wraps geometry that creates culvert head / toe walls
"""
__title__ = "EndWall.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Parameters
from transportationwb import sketch_manager

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def validate_selection():
    """
    Validates the selection and returns the needed elements
    for use in the endwall construction
    """

    structure = Gui.Selection.getSelection()[0]
    selected = Gui.Selection.getSelectionEx()[0]

    if structure.TypeId != 'PartDesign::AdditivePipe':
        print ("Invalid structure selected (requires PartDesign::AdditivePipe")
        return None

    if len(selected.SubElementNames) != 2:
        print ("Invalid number of elements selected.  (select only two)")
        return None

    result = {}

    result["structure"] = structure
    result["edge_name"] = [x for x in selected.SubElementNames if 'Edge' in x][0]
    result["face_name"] = [x for x in selected.SubElementNames if 'Face' in x][0]

    if result["edge_name"] == [] or result["face_name"] == []:
        print ("Invalid geometry selected (requires a face and and edge")
        return None

    for shape in selected.SubObjects:
        if shape.Faces == []:
            result["edge_object"] = shape
        else:
            result["face_object"] = shape

    return result

def vector_compare(vector_1, vector_2):

    sub_vec = vector_1.sub(vector_2)

    print("comparing ")
    print(vector_1)
    print("to")
    print(vector_2)
    print(sub_vec)
    print(sub_vec.Length < 0.00001)
    return sub_vec.Length < 0.00001

class EndWall():

    def __init__(self, obj, parameters):
        """
        Default constructor
        """

        obj.Proxy = self
        self.Type = "EndWall"
        self.Object = obj

        if App.GuiUp:
            _ViewProviderEndWall(obj.ViewObject)

        parameters.Proxy.add_parameter("App::PropertyFloat", "Wall Height", "Height of end wall").Wall_Height = 12.0
        parameters.Proxy.add_parameter("App::PropertyFloat", "Wall Thickness", "Length of wall along culvert").Wall_Thickness = 6.0

        self._add_prop("App::PropertyString", "Library", "path to the sketch library")
        self._add_prop("App::PropertyPythonObject", "SweepBody", "Body defining the structure")
        self._add_prop("App::PropertyPythonObject", "SweepObject", "Sweep defining the solid")
        self._add_prop("App::PropertyPythonObject", "SweepProfile", "Sketch profile")
        self._add_prop("App::PropertyPythonObject", "SweepPath", "Sketch path")
        self._add_prop("App::PropertyPythonObject", "Solid", "Solid resulting from sketch sweep")
        self._add_prop("App::PropertyLength", "Length", "Box culvert length")

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onDocumentRestored(self, fp):
        self.Object = fp

    def _add_prop(self, p_type, p_name, p_desc):

        return self.Object.addProperty(p_type, p_name, "EndWall", QT_TRANSLATE_NOOP("App::Property", p_desc))

    def attach_sketch(self, library_path, sketch_name):
        self.Library = library_path
        self.SweepProfile = sketch_manager.load_sketch(library_path, sketch_name)

    def orient_profile(self,geometry):
        base_edge = geometry["edge_object"]
        base_face = geometry["face_object"]

        point_1 = base_edge.Vertexes[0].Point
        point_2 = base_edge.Vertexes[1].Point

        self.SweepPath = geometry["structure"]

        path_index = -1
        match_count = 0
        target_edge = None

        #determine the profile edge as an edge which shares one endpoint with the base edge
        for edge in base_face.Edges:
            for vertex in edge.Vertexes:
                if (vector_compare(vertex.Point, point_1)) or (vector_compare(vertex.Point, point_2)):
                    match_count += 1

            if match_count == 1:
                target_edge = edge
                break

        point_1 = target_edge.Vertexes[0].Point
        point_2 = target_edge.Vertexes[1].Point

        for i in range(0, len(self.SweepPath.Shape.Edges)):

            match_count = 0

            for vertex in self.SweepPath.Shape.Edges[i].Vertexes:

                if (vector_compare(vertex.Point, point_1)) or (vector_compare(vertex.Point, point_2)):
                    match_count += 1

            if match_count == 2:
                path_index = i
                break

        if path_index == -1:
            print("Unable to find path for sweep")
            return None

        #center the profile on the midopint of the base edge
        midpoint = (point_1 + point_2) / 2.0

        rot = App.Rotation(App.Vector(0,0,1), 0)
        center = App.Vector(0.0, 0.0, 0.0)

        self.SweepProfile.Placement = App.Placement(midpoint, rot, center)

        self.SweepProfile.Support = [(self.SweepPath, "Edge" + str(path_index + 1))]
        self.SweepProfile.MapMode = "NormalToEdge"

        App.ActiveDocument.recompute()

    def sweep_sketch(self, length):
        self.Length = length
        self._do_sweep()

    def _do_sweep(self):

        doc = App.ActiveDocument

        self.SweepBody = doc.addObject("PartDesign::Body", self.SweepProfile.Name + "_Body")

        self.addObject(self.SweepBody)
        doc.recompute()

        self.SweepObject = self.SweepBody.newObject("PartDesign::AdditivePipe", self.SweepProfile.Name + "_Sweep")
        doc.recompute()

        self.SweepObject.Spine = self.SweepPath
        self.SweepObject.Profile = self.SweepProfile
        doc.recompute()

    def onChanged(self, obj, prop):
        #reference does not persist on reload
        if not hasattr(self, "Object"):
            self.Object = obj

    def execute(self, fpy):
        pass

    def addObject(self, child):

        if hasattr(self, "Object"):
            grp = self.Object.Group

            if not child in grp:
                grp.append(child)
                self.Object.Group = grp

class _ViewProviderEndWall:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def claimChildren(self):

        if hasattr(self, "Object"):
            if self.Object:
                if hasattr(self.Object, "Group"):
                    return self.Object.Group
        return []

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        pass

    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        pass

    def getIcon(self):
        return """
/* XPM */
static char * new_alignment_xpm[] = {
"64 64 213 2",
"  	c None",
". 	c #000000",
"+ 	c #090909",
"@ 	c #373836",
"# 	c #333432",
"$ 	c #040404",
"% 	c #4B4C4A",
"& 	c #E4E5E3",
"* 	c #D8D9D5",
"= 	c #BABDB6",
"- 	c #9EA19B",
"; 	c #161615",
"> 	c #EFF0EF",
", 	c #FFFFFF",
"' 	c #C3C6C0",
") 	c #7E807B",
"! 	c #999A98",
"~ 	c #FBFBFA",
"{ 	c #BEC0BA",
"] 	c #A8ABA5",
"^ 	c #181918",
"/ 	c #F8F8F7",
"( 	c #D9DBD7",
"_ 	c #92948F",
": 	c #B9BAB8",
"< 	c #F6F6F6",
"[ 	c #BCBFB8",
"} 	c #3E3F3D",
"| 	c #373736",
"1 	c #FDFDFD",
"2 	c #D1D3CE",
"3 	c #90938D",
"4 	c #010101",
"5 	c #D4D4D2",
"6 	c #F0F1EF",
"7 	c #B9BCB5",
"8 	c #272726",
"9 	c #5B5C5A",
"0 	c #CACCC7",
"a 	c #767874",
"b 	c #030303",
"c 	c #E8E9E7",
"d 	c #E8E9E6",
"e 	c #B3B6B0",
"f 	c #919291",
"g 	c #5D5F5B",
"h 	c #1C1C1C",
"i 	c #F7F7F7",
"j 	c #DDDFDB",
"k 	c #A7AAA3",
"l 	c #080808",
"m 	c #BFC0BE",
"n 	c #F7F8F7",
"o 	c #BDC0B9",
"p 	c #434442",
"q 	c #454544",
"r 	c #D2D4CF",
"s 	c #8F918C",
"t 	c #E0E0DE",
"u 	c #EFF0EE",
"v 	c #B8BBB4",
"w 	c #232422",
"x 	c #888987",
"y 	c #FEFEFE",
"z 	c #C8CAC5",
"A 	c #6C6E6A",
"B 	c #282827",
"C 	c #F8F8F8",
"D 	c #E3E4E1",
"E 	c #ADB0A9",
"F 	c #0E0E0E",
"G 	c #D5D5D4",
"H 	c #BEC1BB",
"I 	c #4A4B48",
"J 	c #80817F",
"K 	c #CED0CB",
"L 	c #93958F",
"M 	c #222221",
"N 	c #E5E6E4",
"O 	c #B5B8B1",
"P 	c #20211F",
"Q 	c #D4D4D3",
"R 	c #F8F9F8",
"S 	c #BFC1BB",
"T 	c #585A56",
"U 	c #9B9D9A",
"V 	c #D0D2CD",
"W 	c #969993",
"X 	c #595959",
"Y 	c #F3F3F2",
"Z 	c #595A57",
"` 	c #2C2C2C",
" .	c #F1F1F0",
"..	c #FAFAFA",
"+.	c #C4C7C1",
"@.	c #90928D",
"#.	c #424241",
"$.	c #F4F4F4",
"%.	c #CACDC7",
"&.	c #AAADA6",
"*.	c #141413",
"=.	c #020202",
"-.	c #919190",
";.	c #FCFCFC",
">.	c #B7BAB3",
",.	c #313230",
"'.	c #151515",
").	c #868786",
"!.	c #EDEDEC",
"~.	c #FBFCFB",
"{.	c #CCCEC9",
"].	c #494A47",
"^.	c #2E2E2E",
"/.	c #646463",
"(.	c #8D8D8C",
"_.	c #AAAAA9",
":.	c #B0B0AE",
"<.	c #BABBB9",
"[.	c #BCBDBB",
"}.	c #BDBEBC",
"|.	c #CACAC8",
"1.	c #EBEBEA",
"2.	c #F2F3F2",
"3.	c #C6C8C2",
"4.	c #313131",
"5.	c #B8B8B7",
"6.	c #FBFBFB",
"7.	c #DCDDDA",
"8.	c #0F0F0F",
"9.	c #B6B7B5",
"0.	c #D8DAD6",
"a.	c #B4B7B0",
"b.	c #474946",
"c.	c #2A2B2A",
"d.	c #EBECEB",
"e.	c #E6E7E5",
"f.	c #DFE0DD",
"g.	c #DBDDD9",
"h.	c #DADCD8",
"i.	c #D6D8D3",
"j.	c #D3D5D0",
"k.	c #9A9C97",
"l.	c #2D2D2C",
"m.	c #EDEEEC",
"n.	c #CDCFCA",
"o.	c #BBBEB7",
"p.	c #A8AAA4",
"q.	c #4E4F4C",
"r.	c #141414",
"s.	c #E9E9E8",
"t.	c #A9ACA6",
"u.	c #7D7F7A",
"v.	c #3C3D3B",
"w.	c #050505",
"x.	c #C5C6C4",
"y.	c #CFD1CC",
"z.	c #757773",
"A.	c #5E605C",
"B.	c #4F504D",
"C.	c #4A4C49",
"D.	c #484947",
"E.	c #2C2C2B",
"F.	c #6F6F6E",
"G.	c #7B7D79",
"H.	c #1B1B1A",
"I.	c #090A09",
"J.	c #ECECEB",
"K.	c #ECEDEB",
"L.	c #555754",
"M.	c #919290",
"N.	c #C2C5BF",
"O.	c #676965",
"P.	c #131413",
"Q.	c #979994",
"R.	c #A7A9A6",
"S.	c #FAFBFA",
"T.	c #292A28",
"U.	c #131313",
"V.	c #F5F5F4",
"W.	c #949592",
"X.	c #F9FAF9",
"Y.	c #BCBFB9",
"Z.	c #1F1F1E",
"`.	c #ECEDEC",
" +	c #DCDEDA",
".+	c #757772",
"++	c #727371",
"@+	c #C0C3BD",
"#+	c #DDDEDC",
"$+	c #E3E4E2",
"%+	c #898B86",
"&+	c #3D3E3C",
"*+	c #C5C7C1",
"=+	c #B8B9B8",
"-+	c #A0A29C",
";+	c #0C0C0C",
">+	c #858684",
",+	c #B6B9B2",
"'+	c #111110",
")+	c #DCDCDB",
"!+	c #DDDEDB",
"~+	c #7D7F7B",
"{+	c #DFE0DE",
"]+	c #FDFDFC",
"^+	c #C1C4BD",
"/+	c #353533",
"(+	c #70726E",
"_+	c #D9DAD6",
":+	c #C9CBC6",
"<+	c #838580",
"[+	c #A3A59F",
"}+	c #222322",
"|+	c #1A1A19",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                            . . . .             ",
"                                                                                                        . . . . . . . .         ",
"                                                                                                      . . . . . . . . . .       ",
"                                                                                                    . . . . + @ # $ . . . .     ",
"                                                                                                    . . . % & * = - ; . . .     ",
"                                                                                                  . . . + > , , ' = ) . . .     ",
"                                                                                                . . . . ! , , ~ { = ] . . . .   ",
"                                                                                                . . . ^ / , , ( = = _ . . . .   ",
"                                                                                              . . . . : , , < [ = = } . . .     ",
"                                                                                              . . . | 1 , , 2 = = 3 4 . . .     ",
"                                                                                            . . . . 5 , , 6 = = 7 8 . . .       ",
"                                                                                            . . . 9 , , , 0 = = a . . . .       ",
"                                                                                          . . . b c , , d = = e ; . . .         ",
"                                                                                        . . . . f , , 1 ' = = g . . . .         ",
"                                                                                        . . . h i , , j = = k l . . .           ",
"                                                                                      . . . . m , , n o = = p . . . .           ",
"                                                                                      . . . q 1 , , r = = s 4 . . .             ",
"                                                                                    . . . 4 t , , u = = v w . . .               ",
"                                                                                  . . . . x , , y z = = A . . . .               ",
"                                                                                  . . . B C , , D = = E F . . .                 ",
"                                                                                . . . 4 G , , / H = = I . . . .                 ",
"                                                                              . . . . J , , , K = = L 4 . . .                   ",
"                                                                              . . . M < , , N = = O P . . .                     ",
"                                                                            . . . 4 Q , , R S = = T . . . .                     ",
"                                                                          . . . . U , , , V = = W $ . . .                       ",
"                                                                        . . . . X 1 , , & = = O P . . . .                       ",
"                                                                      . . . . | i , , Y o = = Z . . . .                         ",
"                                                                  . . . . . `  ., , ..+.= = @.b . . .                           ",
"                                          . . . . . . . . . . . . . . . . #.$., , 1 %.= = &.*.. . . .                           ",
"                                    . . . . . . . . . . . . . . . . . =.-.;., , 1 V = = >.,.. . . .                             ",
"                                  . . . . . . . . . . . . . . . . '.).!., , , ~.{.= = = ].. . . .                               ",
"                              . . . . . . . ^./.(._.:.<.[.}.|.Q 1.y , , , , 2.3.= = = g . . . .                                 ",
"                            . . . . . 4.5.Y , , , , , , , , , , , , , , 6.7.[ = = 7 Z . . . .                                   ",
"                          . . . . 8.9.y , , , , , , , , , , , , , y  .0.S = = = a.b.. . . . .                                   ",
"                        . . . . c.d., , , , 6.u e.f.f.g.h.h.i.j.0 o = = = = = k.M . . . . .                                     ",
"                      . . . . l.2., , , m.n.o.= = = = = = = = = = = = = = p.q.$ . . . . .                                       ",
"                      . . . r.s., , y i.= = = = = = = = = = = = = = t.u.v.w.. . . . .                                           ",
"                    . . . . x., , y y.= = = 7 W z.A.B.C.C.D.} } E.; . . . . . . . .                                             ",
"                    . . . F.y , , 0.= = = G.H.. . . . . . . . . . . . . . . . .                                                 ",
"                  . . . I.J., , K.= = = L.. . . . . . . . . . . . . . . . .                                                     ",
"                . . . . M., , 1 N.= = O.. . . . . . . . . . . . . . .                                                           ",
"                . . . P.2., , f.= = Q.$ . . . .                                                                                 ",
"              . . . . R., , S.S = 7 T.. . . .                                                                                   ",
"              . . . U.V., , ( = = ) . . . .                                                                                     ",
"              . . . W., , X.Y.= v Z.. . .                                                                                       ",
"            . . . w.`., ,  += = .+. . . .                                                                                       ",
"            . . . ++, , 1 @+= = M . . .                                                                                         ",
"          . . . . #+, , $+= = %+. . . .                                                                                         ",
"          . . . &+y , , *+= = @ . . .                                                                                           ",
"          . . . =+, , K.= = -+4 . . .                                                                                           ",
"        . . . ;+i , , V = = L.. . .                                                                                             ",
"        . . . >+, , R o.= ,+'+. . .                                                                                             ",
"        . . . )+, , !+= = ~+. . . .                                                                                             ",
"        . . . {+, ]+^+= = /+. . .                                                                                               ",
"        . . . (+_+:+= = - 4 . . .                                                                                               ",
"        . . . l <+= = [+}+. . .                                                                                                 ",
"        . . . . . |+}+$ . . . .                                                                                                 ",
"          . . . . . . . . . .                                                                                                   ",
"            . . . . . . . .                                                                                                     ",
"                . . . .                                                                                                         ",
"                                                                                                                                ",
"                                                                                                                                "};
"""
#if App.GuiUp:
    #Gui.addCommand("Box-1-Cell", create_1_cell_box())
