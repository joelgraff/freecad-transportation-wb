import FreeCAD as App
import Draft
import Part
import transportationwb

OBJECT_TYPE = "TestFPO"

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide import QtGui, QtCore
    from PySide.QtCore import QT_TRANSLATE_NOOP

def createTestFpo():

    obj = App.ActiveDocument.addObject("App::FeaturePython", OBJECT_TYPE)

    #obj.Label = translate("Transportation", OBJECT_TYPE)

    test_fpo = _TestFPO(obj)

    obj.ViewObject.Proxy = 0

    App.ActiveDocument.recompute()

class widgetHandler(QtGui.QMainWindow):
    def __init__(self, obj):
        super(widgetHandler, self).__init__()

        obj.installEventFilter(self)

    def eventFilter(self, source, event):
        print (source.windowTitle(), event.type())
        return super(widgetHandler, self).eventFilter(source, event)

class _TestFPO():

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = OBJECT_TYPE
        self.Object = obj

        self.add_property("App::PropertyLink", "Link", "Link").Link = App.ActiveDocument.Spreadsheet

        self.init = True

        Gui.ActiveDocument.setEdit(Gui.ActiveDocument.Spreadsheet)

        mw = Gui.getMainWindow()
        mdi = mw.findChild(QtGui.QMdiArea)
        subw = mdi.subWindowList()

        sheet = None

        for i in subw:
            if i.widget().windowTitle() == 'Spreadsheet[*]':
                sheet = i
                break

        self.wHandler = widgetHandler(sheet)

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def add_property(self, prop_type, prop_name, prop_desc):

        return self.Object.addProperty(prop_type, prop_name, OBJECT_TYPE, QT_TRANSLATE_NOOP("App::Property", prop_desc))

    def onChanged(self, obj, prop):

        print('change ', prop)
        pass        
    def execute(self, fpy):

        print("execute ", fpy)

        Gui.updateGui()