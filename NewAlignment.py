import Sketcher
import FreeCAD as App
import Part
import FreeCADGui as Gui
import FeedbackSketcherUtils
import os

class NewAlignment():

    def GetResources(self):

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "/icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Shift+N",
                'MenuText': "New Alignment",
                'ToolTip' : "Create a new alignment and make it active",
                'CmdType' : "ForEdit"}

    def Activated(self):

        if Gui.ActiveDocument == None:
            self._create_document()

        self._set_units()

        self._create_sketches()

        #self._attach_handlers()

        self._add_true_north()

        self._enter_edit_mode()

        self._set_camera(1000.0)

        return

    def IsActive(self):
        return True

    def _attach_handlers(self):
        Gui.ActiveDocument.ActiveView.addDraggable
    def _set_camera(self, height):
        """
        Set the camera to a specific height.  Assumes 2D Orthographic view
        """

        Gui.activeDocument().activeView().setCamera('#Inventor V2.1 ascii \n OrthographicCamera { \n viewportMapping ADJUST_CAMERA \n position 0 0 01 \n orientation 0 0 1 0 \n nearDistance 0 \n farDistance 1 \n aspectRatio 1 \n focalDistance 1 \n height '+str(height)+' }')

    def _enter_edit_mode(self):
        Gui.ActiveDocument.setEdit(Gui.ActiveDocument.Alignment)


    def _set_units(self):
        App.ParamGet("User parameter:BaseApp/Preferences/Units").SetInt("UserSchema", 5)

    def _create_document(self):

        App.newDocument("Unnamed Alignment")
        App.setActiveDocument("Unnamed_Alignment")
        App.ActiveDocument = App.getDocument("Unnamed_Alignment")
        Gui.ActiveDocument = Gui.getDocument("Unnamed_Alignment")

    def _create_sketches(self):

        fbs = FeedbackSketcherUtils.buildFeedbackSketch(
            sketchName="Unnamed_Alignment",
            clientList=['Alignment'])

        return fbs

    def _add_true_north(self):

        sketch = App.ActiveDocument.Alignment

        true_north = Part.LineSegment(
            App.Vector(0.0, 0.0), App.Vector(0.0, 100.0))

        sketch.addGeometry(true_north)
        sketch.addConstraint(Sketcher.Constraint("Vertical", 0))

        App.ActiveDocument.recompute()

Gui.addCommand('NewAlignment',NewAlignment())
