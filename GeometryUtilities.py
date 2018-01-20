import FreeCADGui

class SelectionContainer():
    vertices = []
    lines = []
    curves = []
    pass

def _getSelection():
    #returns a python object which categorizes
    #the selected objects by type
    #Line, Curve, and Vertex

    selected = FreeCADGui.Selection.getSelectionEx()[0].SubObjects
    selLen = len (selected)
    result = SelectionContainer()

    for x in range (0, selLen):
        
        shapeType = selected[x].ShapeType

        if (shapeType == 'Vertex'):
            result.vertices.append (selected[x])

        elif (shapeType == 'Edge'):

            if ('Line' in str(selected[x].Curve)):
                result.lines.append (selected[x])
            else:
                result.curves.append (selected[x])

def _validateSelection():
    #validates the current selections for adding a new element        
    #returns reference to selected element or zero for valid cases

    selLength = len(FreeCADGui.Selection.getSelection())

    result = None

    if selLength == 1:
        geoCount = len (self.ActiveObject)
        result = self.ActiveObject.Geometry [geoCount - 1]

    else:
        result = 0

    return result
