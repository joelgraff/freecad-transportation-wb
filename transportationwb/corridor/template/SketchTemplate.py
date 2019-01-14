

#http://free-cad.sourceforge.net/SrcDocu/dc/d77/classSketcher_1_1SketchObjectPy.html
#https://forum.freecadweb.org/viewtopic.php?t=6121
#https://forum.freecadweb.org/viewtopic.php?t=12829
import FreeCAD as App

class _ViewProvider():
 
    def __init__(self,vobj,icon='/icons/mover.png'):
        self.iconpath =  icon
        self.Object = vobj.Object
        vobj.Proxy = self

    def getIcon(self):
        return self.iconpath


class _Sketch(object):

    def __init__(self,obj,icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
        obj.Proxy = self
        self.Type = self.__class__.__name__
        self.obj2 = obj
        _ViewProvider(obj.ViewObject,icon) 



    def onChanged(proxy,obj,prop):
        proxy.myExecute(obj)


    def myExecute(proxy,obj):

        print('change!!')
        return
        try: fa=App.ActiveDocument.curve
        except: fa=App.ActiveDocument.addObject('Part::Spline','curve')
        fa.Shape=bc.toShape()
        fa.ViewObject.LineColor=(.0,1.0,.0)

        try: ofs=App.ActiveDocument.Offset2D_Out
        except: ofs=App.ActiveDocument.addObject("Part::Offset2D","Offset2D_Out")
        ofs.Source = App.ActiveDocument.curve
        ofs.ViewObject.LineColor=(.0,0.0,1.0)
        ofs.Value = obj.ofout
        ofs.recompute()

        try: ofsi=App.ActiveDocument.Offset2D_In
        except: ofsi=App.ActiveDocument.addObject("Part::Offset2D","Offset2D_In")
        ofsi.Source = App.ActiveDocument.curve
        ofsi.ViewObject.LineColor=(1.0,0.0,.0)
        ofsi.Value = -obj.ofin
        ofsi.recompute()


    def execute(proxy, obj):
        obj.recompute() 
        proxy.myExecute(obj)



#
#
#
#
#

#name="Sole with borders"

obj = App.ActiveDocument.addObject("Sketcher::SketchObjectPython","sop")
#obj.addProperty("App::PropertyInteger","ofin","Base","end").ofin=10
#obj.addProperty("App::PropertyInteger","ofout","Base","end").ofout=10

_Sketch(obj)

#obj.ofin=10
#obj.ofout=10

#App.activeDocument().recompute()
