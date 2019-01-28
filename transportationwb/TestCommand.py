import FreeCAD as App
import FreeCADGui as Gui
import Part


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

    def Activated(self):
        pass

Gui.addCommand('TestCommand', TestCommand())