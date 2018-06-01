#************************************************************************
#*                                                                      *
#*   Copyright (c) 2017                                                 *
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

import FreeCAD
import FreeCADGui as Gui
#import sys
#import TransportationToolbar

import transportationwb
import os, re
global __dir__
__dir__ = os.path.dirname(transportationwb.__file__)


__vers__ = '0.1'

#---------------------


#---------------------------------------------------------------------------
# define the Commands of the Test Application module
#---------------------------------------------------------------------------
class MyTestCmd3:

    def Activated(self):
        import transportationwb.startTests
        reload(transportationwb.startTests)
        transportationwb.startTests.startTests()

    def GetResources(self):
        return {
            'MenuText': 'Unit Tests',
            'ToolTip': 'Runs the self-test for the workbench'
        }

Gui.addCommand('My_Transprtation_Tests', MyTestCmd3())


class DokuTW:

    def Activated(self):
        import WebGui
        fn='https://htmlpreview.github.io/?https://raw.githubusercontent.com/microelly2/freecad-transportation-wb-docu/master/html/index.html'
        WebGui.openBrowser(fn)

    def GetResources(self):
        return {'MenuText': 'Documentation'}

Gui.addCommand('Doku', DokuTW())


#------------------------------------------
# fast command adder template

global _Command


class _Command():

    def __init__(self, lib=None, name=None, icon=None, command=None, modul='transportationwb'):

        if lib == None:
            lmod = modul
        else:
            lmod = modul + '.' + lib
        if command == None:
            command = lmod + ".run()"
        else:
            command = lmod + "." + command

        self.lmod = lmod
        self.command = command
        self.modul = modul
        if icon != None:
            self.icon = __dir__ + icon
        else:
            self.icon = None

        if name == None:
            name = command
        self.name = name

    def GetResources(self):
        if self.icon != None:
            return {'Pixmap': self.icon,
                    'MenuText': self.name,
                    'ToolTip': self.name,
                    'CmdType': "ForEdit"  # bleibt aktiv, wenn sketch editor oder andere tasktab an ist
                    }
        else:
            return {
                #'Pixmap' : self.icon,
                'MenuText': self.name,
                'ToolTip': self.name,
                'CmdType': "ForEdit"  # bleibt aktiv, wenn sketch editor oder andere tasktab an ist
            }

    def IsActive(self):
        if Gui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):

        import re

        # FreeCAD.ActiveDocument.openTransaction("create " + self.name)
        if self.command != '':
            if self.modul != '':
                modul = self.modul
            else:
                modul = self.name
            Gui.doCommand("import " + modul)
            Gui.doCommand("import " + self.lmod)
            Gui.doCommand("reload(" + self.lmod + ")")
            docstring = "print " + re.sub(r'\(.*\)', '.__doc__', self.command)

            Gui.doCommand(docstring)
            Gui.doCommand(self.command)
        # FreeCAD.ActiveDocument.commitTransaction()
        if FreeCAD.ActiveDocument != None:
            FreeCAD.ActiveDocument.recompute()


class _alwaysActive(_Command):

    def IsActive(self):
        return True

# conditions when a command should be active ..


def always():
    ''' always'''
    return True


def ondocument():
    '''if a document is active'''
    return Gui.ActiveDocument != None


def onselection():
    '''if at least one object is selected'''
    return len(Gui.Selection.getSelection()) > 0


def onselection1():
    '''if exactly one object is selected'''
    return len(Gui.Selection.getSelection()) == 1


def onselection2():
    '''if exactly two objects are selected'''
    return len(Gui.Selection.getSelection()) == 2


def onselection3():
    '''if exactly three objects are selected'''
    return len(Gui.Selection.getSelection()) == 3


def onselex():
    '''if at least one subobject is selected'''
    return len(Gui.Selection.getSelectionEx()) != 0


def onselex1():
    '''if exactly one subobject is selected'''
    return len(Gui.Selection.getSelectionEx()) == 1


# the menu entry list
FreeCAD.tcmdsTransportation = []
# create menu entries


def c3b(menu, isactive, name, text, icon=None, cmd=None, *info):

    import re
    global _Command
    if cmd == None:
        cmd = re.sub(r' ', '', text) + '()'
    if name == 0:
        name = re.sub(r' ', '', text)
    t = _Command(name, text, icon, cmd, *info)
    # if title ==0:
    title = re.sub(r' ', '', text)
    name1 = "Transportation_" + title
    t.IsActive = isactive
    Gui.addCommand(name1, t)
    FreeCAD.tcmdsTransportation.append([menu, name1])
    return name1


def c3bG(menu, isactive, name, text, icon=None, cmd=None, *info):

    import re
    global _Command
    if cmd == None:
        cmd = re.sub(r' ', '', text + 'GUI') + '()'
    if name == 0:
        name = re.sub(r' ', '', text + 'GUI')

    t = _Command(name, text, icon, cmd, *info)
    # if title ==0:
    title = re.sub(r' ', '', text)
    name1 = "Transportation_" + title
    t.IsActive = isactive
    Gui.addCommand(name1, t)
    FreeCAD.tcmdsTransportation.append([menu, name1])
    return name1


def c2b(menu, isactive, title, name, text, icon, cmd=None, *info):

    import re
    global _Command
    if cmd == None:
        cmd = re.sub(r' ', '', text) + '()'
    if name == 0:
        name = re.sub(r' ', '', text)
    t = _Command(name, text, icon, cmd, *info)
    if title == 0:
        title = re.sub(r' ', '', text)
    name1 = "Transportation_" + title
    t.IsActive = isactive
    Gui.addCommand(name1, t)
    FreeCAD.tcmds5.append([menu, name1])


if FreeCAD.GuiUp:

    toolbar = []
    toolbar += [c3b(["Simulation"], always, 'vehicle', 'create Vehicle')]
    toolbar += [c3b(["Simulation"], always, 'vehicle', 'create Tailer')]

    toolbar += [c3b(["Simulation", "Submenu"], onselection1,
                    'traffic', 'create swept path', '/../icons/geodesiccircle.svg')]
    toolbar += [c3b(["Simulation", "Submenu"], onselection1,
                    'traffic', 'swept area analysis', '/../icons/draw.svg')]

    terrain = [
        c3b(["Terrain"], onselection1, 'geodesic_lines', 'create Context', '/../icons/draw.svg')]
    terrain += [
        c3b(["Terrain"], onselection1, 'geodesic_lines', 'create something', '/../icons/draw.svg')]

    drainage = [c3b(["Drainage"], always, 'drainage.box_culvert_tools', 'create_1_cell_box')]
    #drainage += [c3b(["Drainage"], always, 'drainage.box_culvert_tools', 'draft_ends')]

    corridor = [c3b(["Corridor"], always, 'corridor.Alignment', 'create_alignment')]
    

    toolbars = [['Simulation', toolbar], ['Terrain', terrain],
               ['Drainage Structure', drainage],
               ['Corridor', corridor],
               ['Tests', ['My_Transprtation_Tests', 'Doku']]]

    c3b(["Demos"], always, 'miki_g', 'test Dialog MainWindow')
    c3b(["Demos"], always, 'miki_g', 'test Dialog Tab')
    c3b(["Demos"], always, 'miki_g', 'test Dialog DockWidget')
    c3b(["Demos"], always, 'miki_g', 'test Dialog')
    c3b(["Demos"], ondocument, 'clipplane', 'demo Clip Plane Animation')

    c3b(["Demos"], always, 'createTestdata', 'create Eichleite')
    c3b(["Demos"], always, 'createTestdata', 'create Woosung')
    c3b(["Demos"], always, 'createTestdata', 'create Japanese Knot')


    c3b(["Curves"], ondocument, 'beziersketch', 'create Bezier Sketch')
    c3b(["Curves"], ondocument, 'beziersketch', 'create Bezier Sketch')
    c3b(["Curves"], ondocument, 'beziersketch', 'create Simple Bezier Sketch')
# not needed and buggy
#    c3b(["Curves"], ondocument, 'beziersketch', 'create Arc Spline')
    c3b(["Curves"], onselection1, 'geodesic_lines', 'create Marker')
    c3b(["Curves"], onselection2, 'stationing', 'combine Curves')

    c3bG(["Labels"], ondocument, 'labeltools', 'create Geo Location')
    c3bG(["Labels"], onselection1, 'labeltools', 'create Stationing')
    c3bG(["Labels"], ondocument, 'labeltools', 'create Graphic Label')
    c3bG(["Labels"], onselection1, 'labeltools', 'create All Labels')
    


#----------------------

class TransportationWorkbench (Workbench):

    MenuText = "Transportation Workbench"
    ToolTip = "A description of my workbench"

    def __init__(self, toolbars, version):

        self.policies_ist = ["Edit..."]
        self.general_fn_list = ["NewAlignment"]
        self.alignment_fn_list = ["Tangent", "Curve1"]
        self.data_source = ["Data Source"]
        #, "Curve2", "Curve3", "CurveSpiral"]

        self.toolbars = toolbars
        self.version = version

    def Initialize(self):

        import NewAlignment
        import Tangent
        import Curve1
        # import Curve2, Curve3, CurveSpiral

        Gui.activateWorkbench("DraftWorkbench")
        Gui.activateWorkbench("SketcherWorkbench")

        self.appendToolbar("Transportation", self.general_fn_list)
        self.appendToolbar("Transportation alignment", self.alignment_fn_list)
        self.appendToolbar("Data Source", self.data_source)
        self.appendMenu("Transportation", self.general_fn_list)
        # self.appendMenu(["Transportation", "Policies"], self.policies_list)
#-------------------

        # create toolbars
        for t in self.toolbars:
            self.appendToolbar(t[0], t[1])

        # create menues
        menues = {}
        ml = []
        for _t in FreeCAD.tcmdsTransportation:
            c = _t[0]
            a = _t[1]
            try:
                menues[tuple(c)].append(a)

            except:
                menues[tuple(c)] = [a]
                ml.append(tuple(c))

        for m in ml:
            self.appendMenu(list(m), menues[m])

        cmds = ['Part_Cone', 'Part_Cylinder', 'Draft_Move', 'Draft_Rotate', 'Draft_Point', 'Draft_ToggleGrid']
        cmds += ['Nurbs_LightOn', 'Nurbs_LightOff']
        self.appendToolbar("My Helpers", cmds)

    def Activated(self):
        Msg("Transportation Workbench version {} activated\n".format(
            self.version))

    def Deactivated(self):
        Msg("Transportation Workbench deactivated\n")

#-------------------
    def ContextMenu(self, recipient):
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("My commands", self.list)

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"

    Icon = """
/* XPM */
static char * workbench_xpm[] = {
"64 64 599 2",
"   c None",
".  c #000000",
"+  c #060606",
"@  c #040404",
"#  c #030303",
"$  c #010101",
"%  c #070706",
"&  c #898B86",
"*  c #888A85",
"=  c #9C9E99",
"-  c #C4C8C1",
";  c #C8CCC5",
">  c #424441",
",  c #080808",
"'  c #807D74",
")  c #E8E8E6",
"!  c #EEEEEC",
"~  c #EAEAE7",
"{  c #D3D1C8",
"]  c #BF9B5D",
"^  c #C17F16",
"/  c #C17D11",
"(  c #C07E15",
"_  c #BF9958",
":  c #8B8D88",
"<  c #A1A39D",
"[  c #C6CAC2",
"}  c #C0C4BC",
"|  c #464746",
"1  c #0A0A09",
"2  c #797977",
"3  c #E7E7E5",
"4  c #EAE4DA",
"5  c #D6B278",
"6  c #C09651",
"7  c #BBB49E",
"8  c #BABDB6",
"9  c #BBB6A3",
"0  c #BE9753",
"a  c #C17E13",
"b  c #C58E35",
"c  c #CACDC6",
"d  c #9B9E98",
"e  c #9EA19B",
"f  c #C5C9C1",
"g  c #383938",
"h  c #0C0C0A",
"i  c #8A8170",
"j  c #EAEAE8",
"k  c #E9E9E7",
"l  c #D2D1C9",
"m  c #C09E64",
"n  c #C18016",
"o  c #C17F15",
"p  c #BBB6A6",
"q  c #CFC9BA",
"r  c #ECEBE7",
"s  c #D3D7CF",
"t  c #ACAFA9",
"u  c #888B85",
"v  c #A1A39E",
"w  c #C7CBC4",
"x  c #B7BAB3",
"y  c #363736",
"z  c #100F0D",
"A  c #8B8B88",
"B  c #EAE4D9",
"C  c #D5B073",
"D  c #C38524",
"E  c #BE9D64",
"F  c #BAB9AC",
"G  c #BAB6A5",
"H  c #C17E14",
"I  c #C78F35",
"J  c #E2D9C8",
"K  c #BDBDBC",
"L  c #0B0B0B",
"M  c #ABB0A9",
"N  c #CACDC4",
"O  c #8F928D",
"P  c #B2B4B1",
"Q  c #C9CAC8",
"R  c #90928E",
"S  c #C8CCC4",
"T  c #B0B3AC",
"U  c #313330",
"V  c #13110D",
"W  c #918778",
"X  c #EBEBE9",
"Y  c #E9E9E6",
"Z  c #D2D4CF",
"`  c #BEB196",
" . c #BE9042",
".. c #C08119",
"+. c #BE9B5E",
"@. c #BCB49D",
"#. c #D5BA8E",
"$. c #ECE9E3",
"%. c #74726E",
"&. c #020201",
"*. c #5E5F5D",
"=. c #D1D5CD",
"-. c #AEB2AC",
";. c #898B85",
">. c #E7E7E6",
",. c #FFFFFF",
"'. c #F6F6F5",
"). c #B5B7B3",
"!. c #A1A49E",
"~. c #282928",
"{. c #949492",
"]. c #EDEDEB",
"^. c #D6B277",
"/. c #C2831E",
"(. c #BE9958",
"_. c #BBB7A5",
":. c #BBAF91",
"<. c #C99643",
"[. c #E5DFD1",
"}. c #C7C7C5",
"|. c #2B2822",
        cmds= ['ZebraTool','ParametricComb','Nurbs_DraftBSpline Editor',
        'Nurbs_Create Shoe','Nurbs_Create Sole','Nurbs_Sole Change Model',
        'Nurbs_scanbackbonecut','Nurbs_createsketchspline','Nurbs_Curves to Face', 'Nurbs_facedraw',
        'Nurbs_createcloverleaf',
        'Part_Cone', 'Part_Cylinder','Draft_Move','Draft_Rotate','Draft_Point','Draft_ToggleGrid',
        'My_Test2','Nurbs_toggleSketch','Sketcher_NewSketch','Nurbs_facedraws','Nurbs_patcha','Nurbs_patchb','Nurbs_folda']

        cmds2=['Nurbs_facedraw','Nurbs_patcha','Nurbs_patchb','Nurbs_folda']

        cmds3=['Nurbs_CreateWorkspace','Nurbs_CreateWSLink','Nurbs_ViewsQV','Nurbs_Views2H','Nurbs_DarkRoom','Nurbs_LightOn','Nurbs_LightOff']
"1. c #151514",
"2. c #B5B8B1",
"3. c #C9CDC4",
"4. c #8E918B",
"5. c #999B96",
"6. c #E0E1DF",
"7. c #E3E4E3",
"8. c #959792",
"9. c #A6A8A2",
"0. c #CACEC6",
"a. c #AAADA7",
"b. c #272726",
"c. c #131313",
"d. c #9C9B99",
"e. c #E9E7E2",
"f. c #D2D3CE",
"g. c #BCB7A2",
"h. c #BDAF90",
"i. c #D7BD92",
"j. c #EDEBE7",
"k. c #8B877D",
"l. c #020202",
"m. c #727570",
"n. c #A7AAA3",
"o. c #B2B3B0",
"p. c #F4F4F4",
"q. c #C0C2BF",
"r. c #A3A69F",
"s. c #C9CCC5",
"t. c #A0A39D",
"u. c #1C1C1B",
"v. c #141413",
"w. c #9B9B9A",
"x. c #EAE5DB",
"y. c #C28118",
"z. c #C08931",
"A. c #BCAB89",
"B. c #BBB39C",
"C. c #BF944D",
"D. c #C07F17",
"E. c #CBAE7C",
"F. c #EAE9E5",
"G. c #D0CFCD",
"H. c #332D24",
"I. c #212221",
"J. c #BEC1BA",
"K. c #C4C9C0",
"L. c #8C8E87",
"M. c #8F918C",
"N. c #B4B5B2",
"O. c #8A8C87",
"P. c #A6A9A3",
"Q. c #CBCFC7",
"R. c #9DA099",
"S. c #1B1B1A",
"T. c #161616",
"U. c #A7A7A6",
"V. c #E8E8E5",
"W. c #D0D1CC",
"X. c #BDBFB6",
"Y. c #BCA87F",
"Z. c #C08527",
"`. c #C08E3D",
" + c #BCB095",
".+ c #BBB298",
"++ c #C29751",
"@+ c #DDC49B",
"#+ c #EEEDEB",
"$+ c #8A8A89",
"%+ c #8A8C86",
"&+ c #D1D4CD",
"*+ c #9FA19C",
"=+ c #CBCFC8",
"-+ c #959992",
";+ c #131413",
">+ c #B1B1B0",
",+ c #E8E4DB",
"'+ c #D5AF71",
")+ c #C28728",
"!+ c #BDA16E",
"~+ c #BABBB1",
"{+ c #BBBCB2",
"]+ c #BDA374",
"^+ c #C0831F",
"/+ c #C17E12",
"(+ c #BF9248",
"_+ c #CAC5B6",
":+ c #D7D5D0",
"<+ c #302D26",
"[+ c #343633",
"}+ c #BBBEB7",
"|+ c #CBD0C8",
"1+ c #878984",
"2+ c #101110",
"3+ c #1D1D1D",
"4+ c #8F8F8E",
"5+ c #E3E4E1",
"6+ c #CED0CB",
"7+ c #BEAE8D",
"8+ c #BF8932",
"9+ c #C08629",TransportationWorkbench
"0+ c #BCA67C",
"a+ c #BBBDB5",
"b+ c #BBB8AB",
"c+ c #C48724",
"d+ c #DDC49A",
"e+ c #949491",
"f+ c #9EA09A",
"g+ c #CDD2CA",
"h+ c #959994",
"i+ c #A8ABA5",
"j+ c #242423",
"k+ c #1D1E1D",
"l+ c #757773",
"m+ c #B8BBB4",
"n+ c #BABCB5",
"o+ c #BCAA84",
"p+ c #C0882F",
"q+ c #C0872C",
"r+ c #C9CBC5",
"s+ c #EBEAE6",
"t+ c #E1DFD9",
"u+ c #53442C",
"v+ c #565955",
"w+ c #B2B6B0",
"x+ c #9FA19D",
"y+ c #91938F",
"z+ c #898D87",
"A+ c #1C1D1C",
"B+ c #1F201F",
"C+ c #7C7E79",
"D+ c #B9BCB5",
"E+ c #BABCB4",
"F+ c #BCA577",
"G+ c #C08424",
"H+ c #C3821A",
"I+ c #DBC6A3",
"J+ c #B1B1AF",
"K+ c #0A0906",
"L+ c #020100",
"M+ c #141414",
"N+ c #B4B8B1",
"O+ c #8D8F8A",
"P+ c #9A9C98",
"Q+ c #F7F7F6",
"R+ c #B7B8B5",
"S+ c #8C8E88",
"T+ c #ADB0A9",
"U+ c #81857F",
"V+ c #1A1A19",
"W+ c #222221",
"X+ c #C8B48D",
"Y+ c #E8DFCF",
"Z+ c #515151",
"`+ c #72746F",
" @ c #787A76",
".@ c #8C8E89",
"+@ c #DBDCDA",
"@@ c #E3E3E2",
"#@ c #9C9E9A",
"$@ c #ABAEA8",
"%@ c #CACEC5",
"&@ c #7B7D79",
"*@ c #292A28",
"=@ c #90918F",
"-@ c #CAC6BB",
";@ c #11100D",
">@ c #242524",
",@ c #C3C7BF",
"'@ c #B0B1AE",
")@ c #F3F4F3",
"!@ c #FAFAFA",
"~@ c #91938E",
"{@ c #ADB0AA",
"]@ c #C8CDC5",
"^@ c #7A7C78",
"/@ c #121312",
"(@ c #373736",
"_@ c #4B4B4B",
":@ c #0A0A0A",
"<@ c #A0A29D",
"[@ c #CFD1CA",
"}@ c #CCCDCA",
"|@ c #DADAD9",
"1@ c #8D908B",
"2@ c #C8CBC4",
"3@ c #747673",
"4@ c #0E0E0E",
"5@ c #313131",
"6@ c #2B2B29",
"7@ c #6F716D",
"8@ c #D2D6CE",
"9@ c #8E918C",
"0@ c #4B4C4A",
"a@ c #4A4740",
"b@ c #DAD5CC",
"c@ c #6B6C6A",
"d@ c #393A38",
"e@ c #BCC0B8",
"f@ c #8C8F8A",
"g@ c #90938D",
"h@ c #B5B9B2",
"i@ c #C2C6BF",
"j@ c #4E514D",
"k@ c #4A4A4A",
"l@ c #DBDBD8",
"m@ c #E0CFB2",
"n@ c #C5C0AF",
"o@ c #111110",
"p@ c #161615",
"q@ c #A2A59F",
"r@ c #C9CDC6",
"s@ c #959791",
"t@ c #91948F",
"u@ c #C1C5BC",
"v@ c #464745",
"w@ c #4D4D4C",
"x@ c #DEDEDC",
"y@ c #EDEDEA",
"z@ c #E1CCAB",
"A@ c #CA933C",
"B@ c #C1821E",
"C@ c #BCAE90",
"D@ c #2A2B29",
"E@ c #6C6E6A",
"F@ c #A3A6A0",
"G@ c #C0C4BD",
"H@ c #595959",
"I@ c #E2E3E0",
"J@ c #DCCAAA",
"K@ c #C88E31",
"L@ c #C18018",
"M@ c #BCA983",
"N@ c #575855",
"O@ c #3F403E",
"P@ c #C7C9C3",
"Q@ c #B3B6AF",
"R@ c #AEB0AC",
"S@ c #ACAEAA",
"T@ c #959691",
"U@ c #B9BDB6",
"V@ c #373936",
"W@ c #616161",
"X@ c #ECECEA",
"Y@ c #DBDCD8",
"Z@ c #C2C4BD",
"`@ c #BCAE91",
" # c #80827D",
".# c #0C0C0B",
"+# c #1E1E1D",
"@# c #C2C5BE",
"## c #8F918D",
"$# c #C5C6C3",
"%# c #D9DAD8",
"&# c #949691",
"*# c #959893",
"=# c #B6B9B3",
"-# c #313231",
";# c #6D6D6C",
"># c #D7D8D3",
",# c #BFC1BB",
"'# c #BE9959",
")# c #212120",
"!# c #CED1CA",
"~# c #9C9D98",
"{# c #BABCB9",
"]# c #F8F9F8",
"^# c #F8F8F7",
"/# c #ABACA9",
"(# c #989B95",
"_# c #BFC3BB",
":# c #AFB1AA",
"<# c #282826",
"[# c #242424",
"}# c #767675",
"|# c #D5D6D2",
"1# c #BEC1BB",
"2# c #BAB8A9",
"3# c #BF8C37",
"4# c #BE9145",
"5# c #BBBBB0",
"6# c #454643",
"7# c #727471",
"8# c #CFD3CB",
"9# c #797B76",
"0# c #959692",
"a# c #DBDBDA",
"b# c #D4D5D3",
"c# c #9A9C96",
"d# c #C1C5BD",
"e# c #ACAEA7",
"f# c #1E1F1E",
"g# c #EAE8E1",
"h# c #D4D3CC",
"i# c #BDC0BA",
"j# c #BF9348",
"k# c #C08A33",
"l# c #BAB7A8",
"m# c #717270",
"n# c #373836",
"o# c #CCCFC8",
"p# c #D2D5CE",
"q# c #848681",
"r# c #A1A39F",
"s# c #9FA29B",
"t# c #171917",
"u# c #D5B176",
"v# c #C3821B",
"w# c #BD9F69",
"x# c #D4D5D1",
"y# c #A6A6A5",
"z# c #151515",
"A# c #C5C8C1",
"B# c #A5A9A1",
"C# c #8C8F89",
"D# c #C09347",
"E# c #BF872A",
"F# c #D9BA88",
"G# c #333331",
"H# c #ADB1AA",
"I# c #ABAEA7",
"J# c #CDD0C8",
"K# c #C08C35",
"L# c #D7B57E",
"M# c #E9E8E4",
"N# c #262624",
"O# c #070707",
"P# c #B6B9B1",
"Q# c #ABADA7",
"R# c #93958F",
"S# c #BF944B",
"T# c #BAB5A2",
"U# c #BBB094",
"V# c #C1831F",
"W# c #D5AF73",
"X# c #E7E6E4",
"Y# c #252420",
"Z# c #050505",
"`# c #B7BBB4",
" $ c #AAADA5",
".$ c #8C8E8A",
"+$ c #050605",
"@$ c #BBB5A1",
"#$ c #D1AF74",
"$$ c #EAE9E6",
"%$ c #272421",
"&$ c #A3A5A0",
"*$ c #F9F9F9",
"=$ c #DADBD9",
"-$ c #90928D",
";$ c #BF8D3A",
">$ c #C0811D",
",$ c #C7C9C4",
"'$ c #3B372E",
")$ c #090A09",
"!$ c #C1C5BE",
"~$ c #969893",
"{$ c #F6F6F6",
"]$ c #F0F0EF",
"^$ c #A0A19D",
"/$ c #BBAC8A",
"($ c #C0882D",
"_$ c #C18525",
":$ c #BCA579",
"<$ c #C0C3BD",
"[$ c #EDEDEC",
"}$ c #555555",
"|$ c #8E8F8A",
"1$ c #E6E6E5",
"2$ c #FBFBFB",
"3$ c #BABBB2",
"4$ c #BF8B34",
"5$ c #BCAE8E",
"6$ c #939392",
"7$ c #343533",
"8$ c #C9CEC6",
"9$ c #CECECC",
"0$ c #E9E9E9",
"a$ c #BABAAE",
"b$ c #D5BA8D",
"c$ c #CACAC9",
"d$ c #787B76",
"e$ c #BCBEB7",
"f$ c #A7A9A5",
"g$ c #9B9D99",
"h$ c #C07D12",
"i$ c #C68928",
"j$ c #ECEBE9",
"k$ c #BABDB5",
"l$ c #979A93",
"m$ c #BCB29A",
"n$ c #BF9041",
"o$ c #DDC59C",
"p$ c #7A766D",
"q$ c #CED2C9",
"r$ c #888A86",
"s$ c #8D8E89",
"t$ c #C89036",
"u$ c #EEEDEA",
"v$ c #DFDEDA",
"w$ c #A4A7A1",
"x$ c #C08421",
"y$ c #DDC296",
"z$ c #625F57",
"A$ c #CFD2CB",
"B$ c #BEBDB2",
"C$ c #EEEDE9",
"D$ c #92948F",
"E$ c #979994",
"F$ c #D1D3CE",
"G$ c #A0A0A0",
"H$ c #222222",
"I$ c #B9BCB4",
"J$ c #E4E4E2",
"K$ c #3B3B3B",
"L$ c #878A85",
"M$ c #BDA476",
        cmds= ['ZebraTool','ParametricComb','Nurbs_DraftBSpline Editor',
        'Nurbs_Create Shoe','Nurbs_Create Sole','Nurbs_Sole Change Model',
        'Nurbs_scanbackbonecut','Nurbs_createsketchspline','Nurbs_Curves to Face', 'Nurbs_facedraw',
        'Nurbs_createcloverleaf',
        'Part_Cone', 'Part_Cylinder','Draft_Move','Draft_Rotate','Draft_Point','Draft_ToggleGrid',
        'My_Test2','Nurbs_toggleSketch','Sketcher_NewSketch','Nurbs_facedraws','Nurbs_patcha','Nurbs_patchb','Nurbs_folda']

        cmds2=['Nurbs_facedraw','Nurbs_patcha','Nurbs_patchb','Nurbs_folda']

        cmds3=['Nurbs_CreateWorkspace','Nurbs_CreateWSLink','Nurbs_ViewsQV','Nurbs_Views2H','Nurbs_DarkRoom','Nurbs_LightOn','Nurbs_LightOff']
"N$ c #0F0F0F",
"O$ c #9FA39D",
"P$ c #90938C",
"Q$ c #060605",
"R$ c #EDEBE5",
"S$ c #636662",
"T$ c #9B9E97",
"U$ c #C28017",
"V$ c #4B4D49",
"W$ c #40413F",
"X$ c #A7AAA2",
"Y$ c #ECEAE4",
"Z$ c #4C4D4B",
"`$ c #A5A89F",
" % c #E5D7BF",
".% c #646561",
"+% c #C1811B",
"@% c #DABB89",
"#% c #656564",
"$% c #A1A69E",
"%% c #C0821C",
"&% c #CA9E57",
"*% c #CCCCC9",
"=% c #272826",
"-% c #BABEB7",
";% c #CCCEC8",
">% c #979995",
",% c #191918",
"'% c #C9CDC5",
")% c #BDB195",
"!% c #C9A973",
"~% c #A8A8A7",
"{% c #BCA375",
"]% c #DEC69E",
"^% c #3C3C3C",
"/% c #222322",
"(% c #BF9754",
"_% c #C68A2B",
":% c #ECE9E2",
"<% c #DBDBD9",
"[% c #8E908C",
"}% c #BDA06E",
"|% c #D8B57B",
"1% c #8E8D8B",
"2% c #767875",
"3% c #ABACA7",
"4% c #BBAC8B",
"5% c #BE9249",
"6% c #C18017",
"7% c #C38218",
"8% c #E7DECE",
"9% c #282727",
"0% c #2A2B2A",
"a% c #BD9F6A",
"b% c #C08729",
"c% c #CE9F53",
"d% c #DDDBD6",
"e% c #BFC3BC",
"f% c #E2CFAF",
"g% c #A19A91",
"h% c #9FA39C",
". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ",
". . + @ @ # $ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . # % % % % % % % % . . ",
". . & * * * * = - ; > $ . . .                                                                   . . . , ' ) ! ~ { ] ^ / ( _ % . ",
". . : * * * * * * < [ } | $ . . .                                                           . . . 1 2 3 ! 4 5 6 7 8 9 0 a b % . ",
". . c d * * * * * * * e f 8 g . . . .                                                   . . . h i j ! k l m n / o 0 p 8 q r % . ",
". . s s t u * * * * * * &
        cmds= ['ZebraTool','ParametricComb','Nurbs_DraftBSpline Editor',
        'Nurbs_Create Shoe','Nurbs_Create Sole','Nurbs_Sole Change Model',
        'Nurbs_scanbackbonecut','Nurbs_createsketchspline','Nurbs_Curves to Face', 'Nurbs_facedraw',
        'Nurbs_createcloverleaf',
        'Part_Cone', 'Part_Cylinder','Draft_Move','Draft_Rotate','Draft_Point','Draft_ToggleGrid',
        'My_Test2','Nurbs_toggleSketch','Sketcher_NewSketch','Nurbs_facedraws','Nurbs_patcha','Nurbs_patchb','Nurbs_folda']

        cmds2=['Nurbs_facedraw','Nurbs_patcha','Nurbs_patchb','Nurbs_folda']

        cmds3=['Nurbs_CreateWorkspace','Nurbs_CreateWSLink','Nurbs_ViewsQV','Nurbs_Views2H','Nurbs_DarkRoom','Nurbs_LightOn','Nurbs_LightOff'] v w x y . . . .                                           . . . z A j ! B C D E F G 0 H / I J ! K $ . ",
". . L M s N O * * * * P Q R & v S T U . . . .                                   . . . V W X ! Y Z `  ./ / ..+.F @.#.$.k %.&.. . ",
". . . . *.=.s -.;.* * >.,.'.).* & !.S t ~.. . . .                           . . . V {.].! 4 ^./.(._.8 :. ./ / <.[.! }.|.. . . . ",
". . . . . 1.2.s 3.4.* 5.6.,.,.7.8.* & 9.0.a.b.. . . .                   . . . c.d.].! e.f.g.0 a / ( 0 _.8 h.i.j.].k.# . .   . . ",
". .     . . l.m.s s n.* * o.p.,.q.* * * & r.s.t.u.. . .           . . . . v.w.! ! x.^.y.z.A.8 B.C.a / D.E.F.! G.H.. . .     . . ",
". .       . . . I.J.s K.L.* M.N.M.* * * * * O.P.Q.R.S.. . . . . . . . T.U.! ! V.W.X.Y.Z./ / `. +8 .+++@+#+! $+l.. .         . . ",
". .           . . @ %+s &+*+* * * * * * * * * * O.P.=+-+;+. . . . T.>+! ! ,+'+)+!+~+8 {+]+^+/ /+(+_+X ! :+<+. . .           . . ",
". .             . . . [+; s }+& * * * * * * * * * * O.P.|+1+2+. . 3+4+5+6+7+8+/ / 9+0+a+8 b++.c+d+! ! e+# . .               . . ",
". .                 . . , f+s g+h+* * * * * * * * * * * O.i+=+O j+. . k+l+m+n+o+p+/ / q+Y.n+r+s+! t+u+. . .                 . . ",
". .                   . . . v+&+s w+;.* * * * * * x+y+* * * : i+0.z+A+. . B+C+D+E+F+G+/ H+I+! ! J+K+. L+                    . . ",
". .                     . . . M+N+s S O+* * * * P+,.Q+R+* * * * S+T+0.U+V+. . W+C+8 {+X+Y+! F.Z+. . .                       . . ",
". .                         . . $ `+s &+ @1+* * .@+@,.,.@@#@* * * * S+$@%@&@v.. . *@=@].! -@;@. . .                         . . ",
". .                           . . . >@,@s n.4.* * * '@)@,.!@~@* * * * * O+{@]@^@/@. . (@_@. . .                             . . ",
". .                           . . . . :@<@s [@<@* * * M.}@|@: * * * * * * * 1@T 2@3@4@. . . .                               . . ",
". .                       . . . . 5@6@. # 7@8@s {@& * * * * * * * * * * * * * * 9@T - 0@l.. . .                             . . ",
". .                   . . . $ a@b@! k c@l.. d@,@s e@f@* * * * * * * * * * * * * * * g@h@i@j@$ . . .                         . . ",
". .               . . . $ k@l@! #+m@n@8 O.o@. p@q@s r@s@* * * * * * * * * * * * * * * * t@2.u@v@$ . . .                     . . ",
". .           . . . $ w@x@! y@z@A@/ B@C@8 9.D@. # E@s =.F@* * * * * * * * * * * * * * * * * y+2.G@v@$ . . .                 . . ",
". .       . . . $ H@I@! ].J@K@/ / / / L@M@8 x N@. . O@P@s Q@O.* * * * * * * R@7.S@* * * * * * * T@8 U@V@. . . .             . . ",
". .   . . . l.W@5+! X@Y@Z@`@B@/ / / / / a !+8 8  #.#. +#t s @###* * * * * * $#,.,.%#&#* * * * * * * *#8 =#-#. . . .         . . ",
". . . . # ;#) ! X@>#,#8 8 8 7 9+/ / / / / / '#E+8 f+)#. , .@s !#~#* * * * * & {#]#,.^#/#* * * * * * * * (#_#:#<#. . . .     . . ",
". $ [#}#) ! X |#1#8 8 8 8 8 8 2#3#/ / / / / / 4#5#8 Q@6#. $ 7#8@8#9#* * * * * * 0#a#,.b#* * * * * * * * * * c#d#e#f#. . . . . . ",
". % ! ! g#h#i#8 8 8 8 8 8 8 8 8 ~+j#/ / / / / / k#l#8 8 m## . n#o#p#q#* * * * * * * r#M.* * * * * * * * * * * * = f s#t#. . . . ",
". % F.u#v#B@w#{+8 8 8 8 8 8 8 8 8 n+E / / / / / / Z.B.x#! y## . z#A#s B#* * * * * * * * * * * * * * * * * * * * * u F@s.C#. . . ",
". % D#/ / / / E#Y.8 8 8 8 8 8 8 8 8 8 ]+H / / / / / F#! X G#. . . 4@_#s H#* * * * * * * * * * * * * * * * * * * * * * O.I#J#. . ",
". % / / / / / / / K#`@8 8 8 8 8 8 8 8 8 M@D./ / / L#! M#N#. .   . . O#P#s Q#* * * * * * * * * * * * * * * * * * * * * * * R#@ . ",
". % / / / / / / / / /+S#T#8 8 8 8 8 8 8 8 U#V#/ W#! X#Y#. .       . . Z#`#s  $* * * * * * * * * * * * * * * * * * * * * * .$+$. ",
". % C./+/ / / / / / / / ( '#F 8 8 8 8 8 8 8 @$#$! $$%$. .           . . O#}+s &$* * * * * * * * * * * 5.*$=$-$* * * * * * .$+$. ",
". % 8 U#;$/ / / / / / / / / >$w#~+8 8 8 8 8 ,$! ! '$. .               . . )$!$s 5.* * * * * * * * * * ~${$,.]$^$* * * * * C#+$. ",
". % 8 8 8 /$($/ / / / / / / / / _$:$n+8 8 <$[$! }$. .                   . . v.8#8@|$* * * * * * * * * * ~$1$,.2$P * * * * C#+$. ",
". % 8 8 8 8 3$]+V#/ / / / / / / / / 4$5$}+1$! 6$. .                       . . 7$s 8$;.* * * * * * * * * * : 9$,.0$* * * * C#+$. ",
". % 8 8 8 8 8 8 a$E n / / / / / / / / / b$! c$$ .                           . . d$s e$* * * * * * * * * * * * f$g$* * * * C#+$. ",
". % 8 8 8 8 8 8 8 8 9 C.h$/ / / / / / i$$.j$c.. .                             . $ k$s l$* * * * * * * * * * * * * * * * * C#+$. ",
". % 8 8 8 8 8 8 8 8 8 8 m$n$/ / / / / o$! p$. .                               . . S.s q$r$* * * * * * * * * * * * * * * * s$+$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 /$p+/ / t$u$v$l..                                   . . O s w$* * * * * * * * * * * * * * * * s$+$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 a+:$x$y$! z$. .                                     . L 8@A$& * * * * * * * * * * * * * * * .@+$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 B$C$Y # .                                       . . D$s E$* * * * * * * * * * * * * * * s$+$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 F$! G$. .                                       . . H$s I$* * * * * * * * * * * * * * * .@+$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 J$! K$. .                                         . . =.=.L$* * * * * * * * * * * * * * .@+$. ",
". % `@/$/$/$/$/$M@Y.Y.Y.Y.Y.M$]+]+x.! N$.                                           . . O$s P$* * * * * * * * * * * * * * .@Q$. ",
". % /+/ / / / / / / / / / / / / / R$! $ .                                           . . S$s T$* * * * * * * * * * * * * * .@Q$. ",
". % H / / / / / / / / / / / / / U$! ! . .                                           . . V$s r.* * * * * * * * * * * * * * .@Q$. ",
". % ^ / / / / / / / / / / / / / y.! ! . .                                             . W$s X$* * * * * * * * * * * * * * .@Q$. ",
". % D./ / / / / / / / / / / / / / Y$! l..                                           . . Z$s `$* * * * * * * * * * * * * * .@Q$. ",
". % ../ / / / / / / / / / / / / /  %! V+.                                           . . .%s f+* * * * * * * * * * * * * * .@Q$. ",
". % +%/ / / / / / / / / / / / / / @%! #%. .                                         . . $%s M.* * * * * * * * * * * * * * .@Q$. ",
". % B@/ / %%%%%%%%%%^+Z.Z.Z.Z.Z.q+&%! *%. .                                         . $ 8#=.1+* * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 j ! 3+.                                       . . =%s -%* * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 ;%! w.. .                                     . . >%s R#* * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 ) X@,%.                                     . N$s '%* * * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 )%!%#+~%. .                                 . . O s c#* * * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 8 8 F {%8+a a ]%! ^%. .                             . . /%s - * * * * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 8 8 8 )%(%..a a a a _%:%<%Z#.                             . l.8 s [%* * * * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 8 8 8 l#}%p+a a a a a a a a |%! 1%. .                         . . 2%s 3%* * * * * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 8 8 a+4%5%6%a a a a a a a a a a 7%8%! 9%. .                     . . 0%8@f * * * * * * * * * * * * * * * * * * * .@Q$. ",
". % 8 8 8 _.a%b%a a a a a a a a a a a a a a c%! d%l.. .                 . . :@e%8#: * * * * * * * * * * * * * * * * * * * .@Q$. ",
". % E+4%5%^ a a a a a a a a a a a a a a a a a f%! g%. .                 . $ !.s h%* * * * * * * * * * * * * * * * * * * * .@Q$. ",
". . + + + + + + + + + + + + + + + % % % % % % % % + . . . . . . . . . . . l.+ + + + + + + + + + + + + + + + + + + + + + + + . . ",
". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . "};
"""


Gui.addWorkbench(TransportationWorkbench(toolbars, __vers__))
