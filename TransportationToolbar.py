from PySide import QtGui
import FreeCADGui as Gui

last = False
mw = Gui.getMainWindow()


def onWorkbenchActivated():

    global last

    active = Gui.activeWorkbench().__class__.__name__

    tb_trans_general = mw.findChild(QtGui.QToolBar, "Transportation")
    tb_trans_align = mw.findChild(QtGui.QToolBar, "Transportation alignment")

    if tb_trans_align and last and active == "SketcherWorkbench":

        tb_trans_general.hide()
        tb_trans_align.show()

        last = False

    elif active == "TransportationWorkbench":

        tb_trans_general.show()
        tb_trans_align.hide()
        last = True

    else:

        last = False

mw.workbenchActivated.connect(onWorkbenchActivated)
