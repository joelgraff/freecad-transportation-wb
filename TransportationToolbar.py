import FreeCADGui as Gui
from PySide import QtGui

last = False
mw = Gui.getMainWindow()


def onWorkbenchActivated():
    global last
    active = Gui.activeWorkbench().__class__.__name__
    tb = mw.findChild(QtGui.QToolBar, "Transportation")

    if tb and last and active == "SketcherWorkbench":
        tb.show()
        last = False
    elif active == "TransportationWorkbench":
        last = True
    elif tb:
        tb.hide()
        last = False
    else:
        last = False

mw.workbenchActivated.connect(onWorkbenchActivated)
