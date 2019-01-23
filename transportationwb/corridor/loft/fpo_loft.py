import Part
import FreeCAD as App

class myLoft(object):
    def __init__(self, obj):
        obj.Proxy = self
        # obj.addProperty("App::PropertyLink", "MasterSketch") <- to build your boxes
        obj.addProperty("App::PropertyFloat","Size")
        obj.Size = 10
    def execute(self,fp):
        size = fp.Size
        boxes = []
        for i in range(0, 10):
            y = float(i) * 100.0
            box = [
                App.Vector(0.0, y, 0.0),
                App.Vector(0.0, y, size),
                App.Vector(size, y, size),
                App.Vector(size, y, 0.0),
                App.Vector(0.0, y, 0.0)
            ]
            boxes += [Part.makePolygon(box)]
        fp.Shape = Part.makeLoft(boxes, False, True, False)

obj = App.ActiveDocument.addObject("Part::FeaturePython","MyLoft")
myLoft(obj)
obj.ViewObject.Proxy = 0
