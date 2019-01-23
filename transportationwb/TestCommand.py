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

    def buildLoft(self, loft, size):

        boxes = []

        for i in range(0, 10):

            y = float(i) * 100.0

            box = [
                App.Vector(0.0, y, 0.0),
                App.Vector(0.0, y, size),
                App.Vector(size, y, size),
                App.Vector(size, y, 0.0),
                App.Vector(0.0, y, 0.0)
            ]

            boxes += [Part.makePolygon(box)]

        if loft is None:
            loft = App.ActiveDocument.addObject('Part::Loft', 'Loft')

        loft.Shape = Part.makeLoft(boxes, False, True, False)

    def testLoftRebuild(self):

        loft = App.ActiveDocument.getObject('Loft')
        size = 10.0

        if loft:
            size = 20.0

        self.buildLoft(loft, size)

        App.ActiveDocument.recompute()

    def Activated(self):
        self.testLoftRebuild()

Gui.addCommand('TestCommand', TestCommand())