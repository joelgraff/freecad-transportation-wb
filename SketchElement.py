import Part
import FreeCAD as App
import Sketcher
import FreeCADGui as Gui
import GeometryUtilities as GeoUtils
import GeometryObjects as GeoObj

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
        result[0][1] - First matched vertex as App.Vector
        """
    
        geo = [constraint.First, constraint.Second, constraint.Third]
        vert = [constraint.FirstPos, constraint.SecondPos, constraint.ThirdPos]
    
        result = []

        for i in range(0, 2):
    
            item = []
        
    	    if geo[i] <= 0:
                continue
        
            geom = sketch.Geometry[geo[i]]
            item.append(geom)
        
            vtx = None
            
            if vert[i] > 0:
                vertices = geom.toShape().Vertexes

                if vert[i] <= len(vertices):
                    vtx = vertices[vert[i] - 1].Point
            
            item.append(vtx)

            result.append(item)
        
        return result
        
    @staticmethod
    def find_attached_geometry(sketch, geometry_index):
        """
        Finds all geometry bound to the passed geometry by constraint

        Arguments:
        geometry - the geometry to match against as a SketchElement or
        Part object

        Returns:
        SketchElement list of all associated geometry
        """

        geom = []

        #iterate the constraints, matching against the passed index
        for constraint in sketch.Constraints:

            indices = [constraint.First, constraint.Second, \
            constraint.Third]

            #if matched, add non-zero indices to the array not including
            #the passed index
            if geometry_index in indices:

                geom.extend(\
                    [idx for _x, idx in enumerate(indices) \
                    if idx > 0 and idx != geometry_index])

        result = []

        #build the SketchElement list and return
        for idx in geom:

            geo = SketchGeometry(sketch, idx)
            result.append(geo)

        return result

    @staticmethod
    def get_binding_constraint(sketch, geo_index_1, geo_index_2):
        """
        Returns the constaint which binds the two geometries

        Arguments:
        geo_index_1 / geo_index_2 - indices of bound geometries

        Returns:
        binding constraint as a SketchConstraint, if found.  None, otherwise
        """

        _tuples = [pair for pair in enumerate(sketch.Constraints)]

        for _tuple in _tuples:

            indices = [_tuple[1].First, _tuple[1].Second, _tuple[1].Third]

            if (geo_index_1 in indices) and (geo_index_2 in indices):
                return SketchConstraint(sketch, _tuple[0])

        return None

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
        match_geo = True
        match_constraint = True
        constraint_types = ["All"]
        result = []
        class_type = None

        if type(vertex) == Part.Vertex:
    	    vertex = vertex.Point

        if type(by_type) == str:
            match_geo = False
            constraint_types = [by_type]
    
        elif type(by_type) == list:
            match_geo = False
            constraint_types = by_type
        
        elif "Part" in str(by_type):
            match_constraint = False
            class_type = by_type
        
        elif "Sketcher" in str(by_type):
            match_geo = False
            class_type = by_type

        if match_geo:
    
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

        if match_constraint:
        
            for i in range(0, sketch.ConstraintCount):
            
                constraint = sketch.Constraints[i]
            
                #filter on constraint type
                if not "All" in constraint_types:

                    if not constraint.type in constraint_types:
                        continue
                
                attached = SketchElement._resolve_constraint(sketch, constraint)

                #match resolved vertices against passed vector
                for item in attached:
                
                    if item[1] == None:
                        continue

                    if GeoUtils.compare_vectors(vertex, item[1]):
                        "selecting constraint: " + str(i)
                        result.append(SketchConstraint(sketch, i))
                        break

        return result

class SketchGeometry(SketchElement):
    """
    Subclass of SketchElement for geometry object types
    """

    def __init__(self, sketch, index):
        SketchElement.__init__(self, sketch, sketch.Geometry[index], index)
        self.line2d = None
        self.arc2d = None

    def match_by_vertex(self, vertex_index, object_type = None):

    	result = SketchElement.find_by_vertex(self.sketch, \
            self.element.toShape().Vertexes[vertex_index], object_type)

        return [_x for _x in result if _x.index != self.index]

    def match_attached_geometry(self):
        """
        Returns the geometry attached to the SketchGeometry element
        """
        return SketchElement.find_attached_geometry(self.sketch, self.index)

    def get_binding_constraint(self, geometry_index):
        """
        Returns the constraint which binds the SketchGeometry element to the
        passed geometry

        Arguments:
        geometry_index - index of bound geometry 
        """
        return SketchElement.get_binding_constraint(self.sketch, self.index, \
            geometry_index)

    def as_line2d(self):
        """
        Returns a Part.LineSegment as a Line2d object, None otherwise
        """

        if self.line2d == None:
            if self.type == Part.LineSegment:
                self.line2d = GeoObj.Line2d.from_line_segment(self.element)

        return self.line2d

    def as_arc2d(self):
        """
        Returns a Part.ArcOfCircle as an Arc2d object, None otherwise
        """

        if self.arc2d == None:
            if self.type == Part.ArcOfCircle:
                self.arc2d = GeoObj.Arc2d(self.element)

        return self.arc2d

class SketchConstraint(SketchElement):
    """
    Subclass of SketchElement for constraint object types
    """

    def __init__(self, sketch, index):
        SketchElement.__init__(self, sketch, \
        sketch.Constraints[index], index)
