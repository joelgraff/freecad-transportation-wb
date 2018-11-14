import FreeCAD as App
import Draft
import Part
import transportationwb

OBJECT_TYPE = "TestFPO"

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def createTestFpo():

    obj = App.ActiveDocument.addObject("App::FeaturePython", OBJECT_TYPE)

    #obj.Label = translate("Transportation", OBJECT_TYPE)

    test_fpo = _TestFPO(obj)

    _ViewProviderCell(obj.ViewObject)

    App.ActiveDocument.recompute()

class _TestFPO():

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = OBJECT_TYPE
        self.Object = obj

        self.add_property("App::PropertyLength", "StartStation", "Starting station for the cell").StartStation = 0.00
        self.add_property("App::PropertyLength", "EndStation", "Ending station for the cell").EndStation = 0.00
        self.add_property("App::PropertyLength", "Length", "Length of baseline").Length = 0.00

        self.init = True

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def add_property(self, prop_type, prop_name, prop_desc):

        return self.Object.addProperty(prop_type, prop_name, OBJECT_TYPE, QT_TRANSLATE_NOOP("App::Property", prop_desc))

    def onChanged(self, obj, prop):

        if not hasattr(self, 'init'):
            return

        print ("property " + prop)
        print (prop)

        prop_obj = obj.getPropertyByName(prop)

        if prop in ["StartStation", "EndStation"]:

            print ("updating property " + prop)
            self.Object.Length = self.Object.EndStation - self.Object.StartStation

        Gui.updateGui()

        if not hasattr(self, "Object"):
            self.Object = obj

    def execute(self, fpy):

        print("execute")

        Gui.updateGui()

class _ViewProviderCell:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None
    
    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        print("update data " + prop)
    
    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        print ("View property changed " + prop)