import FreeCAD as App
import FreeCADGui as Gui

from transportationwb.corridor.loft import LoftGroup

class TestCommand():
    '''
    A command for testing
    '''
    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        return {'Pixmap'  : '',
                'Accel'   : '',
                'MenuText': "Test Command",
                'ToolTip' : "Command for testing",
                'CmdType' : "ForEdit"}

    def buildLinkedLoft(self):
        '''
        Test the loft DocumentObjectGroupPython class linking with a sketch
        '''

        _lg = LoftGroup.createLoftGroup('test_loft', App.ActiveDocument.Sketch)

    def Activated(self):
        self.buildLinkedLoft()

Gui.addCommand('TestCommand', TestCommand())