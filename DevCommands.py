import FreeCADGui as Gui
from importlib import reload
import FreeCAD
import os
import transportationwb

global __dir__
__dir__ = os.path.dirname(transportationwb.__file__)

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
            Gui.doCommand("import importlib")
            Gui.doCommand("importlib.reload(" + self.lmod + ")")
            docstring = "print " + re.sub(r'\(.*\)', '.__doc__', self.command)

           # Gui.doCommand(docstring)
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

    #drainage = [c3b(["Drainage"], always, 'drainage.box_culvert_tools', 'add_1_cell_box')]
    #drainage += [c3b(["Drainage"], always, 'drainage.box_culvert_tools', 'draft_ends')]
    #drainage += [c3b(["Drainage"], always, 'drainage.box_culvert_tools', 'add_headwall')]
    #drainage += [c3b(["Drainage"], always, 'drainage.box_culvert_tools', 'add_toewall')]
    #drainage += [c3b(["Drainage"], always, "drainage.Parameters", "add parameter")]

    #corridor = [c3b(["Corridor"], always, 'corridor.Alignment', 'create_alignment')]
    #corridor += [c3b(["Corridor"], always, 'corridor.Cell', 'createCell')]


    FreeCAD.transportation_toolbars = [
        ['Simulation', toolbar], 
        ['Terrain', terrain],
       #['Drainage Structure', drainage],
       #['Corridor', corridor],
        ['Tests', ['My_Transprtation_Tests', 'Doku']]
    ]

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