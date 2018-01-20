import FreeCADGui as Gui
import FreeCAD as App
from PySide import QtGui

mw = Gui.getMainWindow()
p = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Transportation")


def onWorkbenchActivated():
    last = p.GetBool("last", 0)
    active = Gui.activeWorkbench().__class__.__name__
    tb = mw.findChild(QtGui.QToolBar, "Transportation")

    if tb and last and active == "SketcherWorkbench":
        tb.show()
        p.SetBool("last", 0)
    elif active == "TransportationWorkbench":
        p.SetBool("last", 1)
    elif tb:
        tb.hide()
        p.SetBool("last", 0)
    else:
        p.SetBool("last", 0)

mw.workbenchActivated.connect(onWorkbenchActivated)
