from PySide import QtGui, QtCore
import FreeCAD as App
import FreeCADGui as Gui

userCancelled = "Cancelled"
userOk = "OK"

class SweepPicker(QtGui.QMainWindow):

    class SelectionObserver:

        def setDialog(self, dialog):
            self.dialog = dialog

        def addSelection(self,doc,obj,sub,pos):

            if self.dialog is None:
                return

            self.dialog.txt_edge.setText(obj+'.'+sub)

            App.Console.PrintMessage("Document: %s, Object: %s, Element: %s, Pos: (%d,%d,%d)\n" % (doc,obj,sub, pos[0], pos[1], pos[2]))

    def __init__(self):
        super(SweepPicker, self).__init__()
        self.initUI()

    def _get_sketch_list(self):

        result  = []

        for obj in App.ActiveDocument.Objects:
            if type(obj).__name__=='SketchObject':
                result.append(obj.Label)

        return result

    def _kill(self, accept = False):

        self.result = userCancelled

        if accept:
            self.result = userOk

        Gui.Selection.removeObserver(self.observer)
        self.close()

    def onCancel(self):
        self._kill()

    def onOk(self):
        self._kill(True)

    def onSketchPopup(self, selected_text):
        self.selected_sketch = selected_text

    def closeEvent(self, event):
        event.accept()
        self._kill()

    def initUI(self):

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(250, 250, 320, 190)
        self.setWindowTitle("Our Example Nonmodal Program Window")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)

        self.result = userCancelled

        self.observer = self.SelectionObserver()
        self.observer.dialog = self
        Gui.Selection.addObserver(self.observer)

        #create template sketch picker ui
        self.label1 = QtGui.QLabel("Template sketch:", self)
        self.label1.move(20, 20)

        #create sweep edge picker ui
        self.label2 = QtGui.QLabel("Sweep edge:", self)
        self.label2.move(20, 60)

        self.txt_edge = QtGui.QLineEdit(self)
        self.txt_edge.setText("")
        self.txt_edge.setFixedWidth(280)
        self.txt_edge.move(20, 95)

        #sketch dropdown
        sketch_list = self._get_sketch_list()
        self.selected_sketch = sketch_list[0]

        self.sketch_popup = QtGui.QComboBox(self)
        self.sketch_popup.addItems(sketch_list)
        self.sketch_popup.activated[str].connect(self.onSketchPopup)
        self.sketch_popup.move(195, 20)

        #cancel button
        self.cancelButton = QtGui.QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.cancelButton.move(80, 145)

        #ok button
        self.okButton = QtGui.QPushButton('Ok', self)
        self.okButton.clicked.connect(self.onOk)
        self.okButton.move(200, 145)

        self.show()

    def setObject(self, obj):

        if type(obj.Object).__name__ == 'SketchObject':
            if not obj.HasSubObjects:
                self.dialog.txtSketch = obj.Name
            else:
                self.dialog.txtEdge = obj.SubObjects[0].Name
        
        elif obj.HasSubObjects:
            self.dialog.txtEdge = obj.SubObjects[0]

    def findObjects(self):

        for obj in Gui.Selection.getSelectionEx():
            self.setObject(obj)

def show_dialog():

    return SweepPicker()