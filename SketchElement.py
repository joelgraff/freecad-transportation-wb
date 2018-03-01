import Part
import FreeCAD as App
import Sketcher
import FreeCADGui as Gui
import GeometryUtilities as GeoUtils

class SketchElement(object):
    """
    A data type for storing the active selection by the types of objects 
    selected.
    """

    def __init__(self, sketch, element, index):
        self.element = element
        self.index = index
        self.type = type(self.element)
        self.sketch = sketch
    
    def match_by_vertex(self):
    	SketchElement.find_by_vertex(self.sketch, \
    	self.element.toShape().Vertexes[self.index].Point)

    def match_attached_geometry(self):
        SketchElement.find_attached_geometry(self.sketch, self.element)
    
    @staticmethod
    def _resolve_constraint(sketch, constraint):
        """
        Resolves any references in the passed element to geometry and vertex
        vectors
    
        Arguments:
        sketch - reference to the containing sketch
        constraint - A Sketcher constraint
    
        Returns:
        List of geometry / vertex pairs accessible as:
        result[0][0] - First matched geometry
        result[0][1] - First matched vertex
        """
    
        geo = [constraint.First, constraint.Second, constraint.Third]
        vert = [constraint.FirstPos, constraint.SecondPos, constraint.ThirdPos]
    
        result = []

        for i in range(0, 2):
    
            item = []
        
    	    if geo[i] == 0:
                continue
        
            item.append(sketch.Geometry[geo[i]])
        
            if vert[i] > 0:
                vert = geo[i].toShape().Vertexes[vert[i]]
            
            item.append(vert)

            result.append(item)
        
        return result
        
    @staticmethod
    def find_attached_geometry(sketch, geometry):
        """
        Finds all geometry bound to the passed geometry by constraint

        Arguments:
        geometry - the geometry to match against as a SketchElement or
        Part object

        Returns:
        SketchElement list of all associated geometry
        """

    @staticmethod
    def find_by_vertex(sketch, vertex, by_type = None):
        """
        Finds all elements which reference a vertex matching the passed vector
    
        Arguments:
        sketch - Reference to the containing sketch object
        vertex - Vertex to match against as an App.Vector or as Part.Vertex
        by_type (optional) - value data type may be a class type or a
        string 
            - [class] - a Part object or Sketcher.Constraint.
            - [String / List] (Constraint Only) - The constraint type:
            "Tangent", "PointOnObject", "Coincident", etc.
            
        Returns:
        list of SketchElements containing the matched geometry / constraints
        """
    
        if type(vertex) == Part.Vertex:
    	    vertex = vertex.Point
    	
            result = []
            match_geo = True
            match_constraint = True
            constraint_type = ["All"]
            class_type = None
    
        if type(by_type) == str:
            match_geo = False
            constraint_type = [by_type]
    
        elif type(by_type) == list:
            match_geo = False
            constraint_type = by_type
        
        elif "Part" in str(type(by_type)):
            match_constraint = False
            class_type = by_type
        
        elif "Sketcher" in str(type(by_type)):
            match_geo = False
            class_type = by_type
        
        if (match_geo):
    
            for i in range(0, len(sketch.Geometry)):

                geo = sketch.Geometry[i]
            
                #filter on geometry class
                if (class_type != None):
                    if type(geo) != class_type:
                        continue

                #match geometry vertices against passed vector                
                for vtx in geo.toShape().Vertexes:
                
                    if GeoUtils.compare_vectors(vtx.Point, vertex):
                        result.append(SketchGeometry(sketch, i))
                        break
    
            
        if (match_constraint):
        
            for i in range(0, sketch.ConstraintCount):
            
                constraint = sketch.Constraint[i]
            
                #filter on constraint type
                if constraint_type != "All":
                    if not constraint_type in constraint.Content:
                        continue
                
                attached = SketchElement._resolve_constraint(sketch, constraint)
            
                #match resolved vertices against passed vector
                for item in attached:
                
                    if item[1] == None:
                        continue
                
                    if GeoUtils.compare_vectors(vertex, item[1].Point):
                        result.append(SketchConstraint(sketch, i))
                        break
                
        return result

class SketchGeometry(SketchElement):
    """
    Subclass of SketchElement for geometry object types
    """

    def __init__(self, sketch, index):
        SketchElement.__init__(sketch, sketch.Geometry[index], index)

class SketchConstraint(SketchElement):
    """
    Subclass of SketchElement for constraint object types
    """

    def __init__(self, sketch, index):
        SketchElement.__init__(sketch, sketch.Constraint[index], index)
