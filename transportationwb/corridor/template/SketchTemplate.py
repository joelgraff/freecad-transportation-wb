

#http://free-cad.sourceforge.net/SrcDocu/dc/d77/classSketcher_1_1SketchObjectPy.html
#https://forum.freecadweb.org/viewtopic.php?t=6121
#https://forum.freecadweb.org/viewtopic.php?t=12829
import FreeCAD as App

if App.Gui:
    import FreeCADGui as Gui
    from PySide.QtCore import QT_TRANSLATE_NOOP

def create(sketch_object, template_name):
    '''
    Constructor method foor creating a new sketch template
    '''

    obj = App.ActiveDocument.addObject("Sketcher::SketchObjectPython", template_name)

    _o = _Sketch(obj)
    _o.duplicate(sketch_object)

    App.activeDocument().recompute()

    return _o

class _Sketch(object):

    def __init__(self, obj, icon=''):
        obj.Proxy = self
        self.Type = self.__class__.__name__
        self.Object = obj

        _ViewProvider(obj.ViewObject, icon)

        self._add_property('LinkList', 'Lofts', 'List of dependent lofts', isReadOnly=True)

    def duplicate(self, sketch):
        '''
        Duplicate the source sketch in the SketchObjectPython
        '''

        for geo in sketch.Geometry:
            index = self.Object.addGeometry(geo)
            self.Object.setConstruction(index, geo.Construction)

        for constraint in sketch.Constraints:
            self.Object.addConstraint(constraint)

        self.Object.Placement = sketch.Placement

        for expr in sketch.ExpressionEngine:
            self.Object.setExpression(expr[0], expr[1])

        self.Object.solve()
        self.Object.recompute()

    def _add_property(self, p_type, name, desc, default_value=None, isReadOnly=False):
        '''
        Build FPO properties

        p_type - the Property type, either using the formal type definition ('App::Propertyxxx') 
                 or shortended version
        name - the Property name.  Groups are defined here in 'Group.Name' format.  
               If group is omitted (no '.' in the string), the entire string is used 
               as the name and the default group is the object type name
        desc - tooltip description
        default_value - default property value
        isReadOnly - sets the property as read-only
        '''

        tple = name.split('.')

        p_name = tple[0]
        p_group = 'Base'

        if len(tple) == 2:
            p_name = tple[1]
            p_group = tple[0]

        if p_type == 'Length':
            p_type = 'App::PropertyLength'

        elif p_type == 'Float':
            p_type = 'App::PropertyFloat'

        elif p_type == 'Bool':
            p_type = 'App::PropertyBool'

        elif p_type == 'Link':
            p_type = 'App::PropertyLink'

        elif p_type == 'LinkList':
            p_type = 'App::PropertyLinkList'

        elif p_type == 'Distance':
            p_type = 'App::PropertyDistance'

        elif p_type == 'Percent':
            p_type = 'App::PropertyPercent'

        else:
            print ('Invalid property type specified: ', p_type)
            return None

        self.Object.addProperty(p_type, p_name, p_group, QT_TRANSLATE_NOOP("App::Property", desc))

        prop = self.Object.getPropertyByName(p_name)

        if p_type in [
                'App::PropertyFloat',
                'App::PropertyBool',
                'App::PropertyPercent',
                'App::PropertyLinkList'
            ]:
            prop = default_value
        else:
            prop.Value = default_value

        if isReadOnly:
            self.Object.setEditorMode(p_name, 1)

        return prop


    def onChanged(self, obj, prop):

        #avoid call during object initializtion
        if not hasattr(self, 'Object'):
            return

        self.myExecute(obj)


    def myExecute(self, obj):

        if self.Object.Lofts:
            pass
#        try: fa=App.ActiveDocument.curve
#        except: fa=App.ActiveDocument.addObject('Part::Spline','curve')
#        fa.Shape=bc.toShape()
#        fa.ViewObject.LineColor=(.0,1.0,.0)

class _ViewProvider():

    def execute(self, obj):
        obj.recompute()
        self.myExecute(obj)

    def __init__(self, vobj, icon='/icons/mover.png'):
        self.iconpath =  icon
        self.Object = vobj.Object
        vobj.Proxy = self

    def getIcon(self):
        return self.iconpath
