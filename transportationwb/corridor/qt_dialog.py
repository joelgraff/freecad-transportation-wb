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

            self.dialog.edge_object = obj
            self.dialog.edge_name = sub
            self.dialog.lbl_edge.setText(obj+'.'+sub)
            self.dialog.updateSweep()
            self.dialog.parent.recompute()

    def __init__(self, parent):
        super(SweepPicker, self).__init__()
        self.parent = parent
        self.createCallback = None
        self.destroyCallback = None
        self.cell_name = "Cell"
        self.edge_object = ""
        self.edge_name = ""
        self.selected_sketch = ""

        self.initUI()

    def _get_sketch_list(self):

        result  = ["None"]

        for obj in App.ActiveDocument.Objects:
            if type(obj).__name__=='SketchObject':
                result.append(obj.Label)

        return result

    def updateSweep(self):

        self.destroyCallback(self.cell_name)

        result = self.createCallback(self.cell_name, self.selected_sketch, self.edge_object, self.edge_name)

        if result is None:
            return

        self.name_text.setText(result.Name)
        self.parent.recompute()

    def onCancel(self):
        self.destroyCallback(self.cell_name)
        self.close()

    def onOk(self):
        self.result = userOk
        self.close()

        #self.updateSweep()

    def onSketchPopup(self, selected_text):
        self.selected_sketch = selected_text
        self.updateSweep()

    def onLineEditDone(self):
        self.cell_name = self.name_text.text()
        self.updateSweep()

    def onStarStaChange(self, value):
        pass
    
    def onEndStaChange(self, value):
        pass

    def onResolutionChange(self, value):
        pass

    def closeEvent(self, event):

        event.accept()
        Gui.Selection.removeObserver(self.observer)

        if self.result == userCancelled:
            self.destroyCallback(self.cell_name)

    def initUI(self):

        # create our window
        # define window		xLoc,yLoc,xDim,yDim
        self.setGeometry(250, 250, 270, 185)
        self.setWindowTitle("Our Example Nonmodal Program Window")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMouseTracking(True)

        self.result = userCancelled

        #create cell name widgets
        self.name_label = QtGui.QLabel("Cell Name:", self)
        self.name_label.move(20, 20)

        self.name_text = QtGui.QLineEdit(self.cell_name, self)
        self.name_text.setFixedWidth(100)
        self.name_text.move(150, 20)
        self.name_text.editingFinished.connect(self.onLineEditDone)

        #create template sketch picker widgets
        self.label1 = QtGui.QLabel("Template sketch:", self)
        self.label1.move(20, 60)

        sketch_list = self._get_sketch_list()
        self.selected_sketch = sketch_list[0]

        self.sketch_popup = QtGui.QComboBox(self)
        self.sketch_popup.addItems(sketch_list)
        self.sketch_popup.activated[str].connect(self.onSketchPopup)
        self.sketch_popup.move(150, 60)

        #create sweep edge picker widgets
        self.label2 = QtGui.QLabel("Sweep edge:", self)
        self.label2.move(20, 100)

        self.lbl_edge = QtGui.QLabel("", self)
        self.lbl_edge.setText("")
        self.lbl_edge.setFixedWidth(280)
        self.lbl_edge.move(150, 100)

        #create spinners for start / end stations and resolution
        self.lbl_start_sta = QtGui.QLabel("Start station", self)
        self.lbl_start_sta = QtGui.QLabel.move(20, 140)

        self.spb_start_sta = QtGui.QSpinBox(self)
        self.spb_start_sta.value = 0.00
        self.spb_start_sta.move(150, 140)
        self.spb_start_sta.activated[int].connect(self.onStartStaChange)

        self.lbl_end_sta = QtGui.QLabel("End station", self)
        self.lbl_end_sta = QtGui.QLabel.move(20, 180)
        
        self.spb_end_sta = QtGui.QSpinBox(self)
        self.spb_end_sta.value = 0.00
        self.spb_end_sta.move(150, 180)
        self.spb_end_sta.activated[int].connect(self.onEndStaChange)

        self.lbl_resolution = QtGui.QLabel("Resolution", self)
        self.lbl_resolution = QtGui.QLabel.move(20, 220)
        
        self.spb_resolution = QtGui.QSpinBox(self)
        self.spb_resolution.value = 0.00
        self.spb_resolution.move(150, 220)
        self.spb_resolution.activated[int].connect(self.onResolutionChange)

        #cancel button
        self.cancelButton = QtGui.QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.onCancel)
        self.cancelButton.setAutoDefault(True)
        self.cancelButton.setFixedWidth(60)
        self.cancelButton.move(120, 140)

        #ok button
        self.okButton = QtGui.QPushButton('Ok', self)
        self.okButton.clicked.connect(self.onOk)
        self.okButton.setFixedWidth(60)
        self.okButton.move(190, 140)

        self.observer = self.SelectionObserver()
        self.observer.dialog = self

        Gui.Selection.addObserver(self.observer)

        print(self.lbl_edge.text())
        print(self.observer.dialog.lbl_edge.text())
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