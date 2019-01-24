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
        prop_list = [
            'App::PropertyBool',
            'App::PropertyBoolList',
            'App::PropertyFloat',
            'App::PropertyFloatList',
            'App::PropertyFloatConstraint',
            'App::PropertyQuantity',
            'App::PropertyQuantityConstraint',
            'App::PropertyAngle',
            'App::PropertyDistance',
            'App::PropertyLength',
            'App::PropertySpeed',
            'App::PropertyAcceleration',
            'App::PropertyForce',
            'App::PropertyPressure',
            'App::PropertyInteger',
            'App::PropertyIntegerConstraint',
            'App::PropertyPercent',
            'App::PropertyEnumeration',
            'App::PropertyIntegerList',
            'App::PropertyIntegerSet',
            'App::PropertyMap',
            'App::PropertyString',
            'App::PropertyUUID',
            'App::PropertyFont',
            'App::PropertyStringList',
            'App::PropertyLink',
            'App::PropertyLinkSub',
            'App::PropertyLinkList',
            'App::PropertyLinkSubList',
            'App::PropertyMatrix',
            'App::PropertyVector',
            'App::PropertyVectorList',
            'App::PropertyPlacement',
            'App::PropertyPlacementLink',
            'App::PropertyColor',
            'App::PropertyColorList',
            'App::PropertyMaterial',
            'App::PropertyPath',
            'App::PropertyFile',
            'App::PropertyFileIncluded',
            'App::PropertyPythonObject',
            'Part::PropertyPartShape',
            'Part::PropertyGeometryList',
            'Part::PropertyShapeHistory',
            'Part::PropertyFilletEdges',
            'Sketcher::PropertyConstraintList'
        ]

        x = App.ActiveDocument.addObject('Part::FeaturePython', 'fpo')

        for prop in prop_list:
            p_name = prop.replace('App::Property', '')
            p_name = p_name.replace('Part::Property', '')
            p_name = p_name.replace('Sketcher::Property', '')

            x.addProperty(prop, p_name, p_name)

        App.ActiveDocument.recompute()

Gui.addCommand('TestCommand', TestCommand())