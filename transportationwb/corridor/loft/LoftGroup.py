
# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

'''
AddProperty helper function for FeaturePythonObjects
'''

__title__ = "LoftGroup.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Part
from transportationwb import ScriptedObjectSupport as Sos

def createLoftGroup(parent, group_name, spline, sketch, local_sketch):
    '''
    Constructor method for loft group
    '''

    obj = parent.newObject("App::DocumentObjectGroupPython", group_name)

    #duplicate the sketch and include it in the loft group
    #then set the link to the local sketch
    if local_sketch:

        sketch = App.ActiveDocument.copyObject(sketch, False)
        obj.addObject(sketch)

    fpo = _LoftGroup(obj, spline, sketch)
    _ViewProviderLoftGroup(obj.ViewObject)

    return fpo

class _LoftGroup():

    def __init__(self, obj, spline, sketch):
        self.Enabled = False
        self.Type = "_LoftGroup"
        self.Object = obj

        obj.Proxy = self

        Sos._add_property(self, 'Link', 'Spline', 'Linked spline', spline)
        Sos._add_property(self, 'Link', 'Sketch', 'Linked sketch', sketch)
        Sos._add_property(self, 'Float', 'Interval', 'Section spacing interval', 100.0)

        self.Enabled = True

    def _build_sections(self, spline, sketch):
        '''
        Generate / regenerate the loft based on the linked sketch and parameters
        '''

        #reference spline curve object
        curve = spline.Shape.Curve

        #return first / last parameters
        [a, b]=spline.Shape.ParameterRange

        #round the length up and add one
        length = int(round(b)) + 1

        comps = []
        z_up = App.Vector(0, 0, 1)

        #iterate the range of the length as integers
        i = 0.0
        step = 304.8 * float(self.Object.Interval)

        print ('interval = ', self.Object.Interval)
        print ('step = ', step)
        sketch_points = []

        for vtx in sketch.Shape.Vertexes:
            sketch_points.append(vtx.Point)

        is_last_section = False

        while i <= length:

            normal = curve.tangent(i)[0].cross(z_up).normalize()

            #get the coordinate of the sweep path at the first millimeter
            origin = curve.value(i)

            #get the tangent of the sweep path at that coordinate
            tangent = curve.tangent(i)

            #calculate the normal against z-up and normalize
            x_normal = tangent[0].cross(z_up).normalize()
            z_normal = tangent[0].cross(x_normal).normalize()

            #z-coordinate should always be positive
            if z_normal.z < 0.0:
                z_normal = z_normal.negative()

            poly_points = []

            for point in sketch_points:
                poly_points.append(origin + (point.x * normal) + (point.y * z_normal))

            poly_points.append(origin)

            #generate a polygon of the points and save it
            comps += [Part.makePolygon(poly_points)]

            i += step

            if (not is_last_section) and (i > length):
                i = length
                is_last_section = True

        return comps

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def _get_child(self, object_type):
        '''
        Test for a spline, either linked or local
        '''
        for obj in self.Object.Group:
            if obj.TypeId == object_type:
                return obj

        return None

    def _get_support(self):
        '''
        Return the supporting spline and sketch for generating the loft
        '''

        spline = self._get_child('Part::Part2DObjectPython')
        sketch = self._get_child('Sketcher::SketchObjectPython')

        #if spline is None:
        spline = self.Object.Spline

        if spline is None:
            print('Missing linked or local spline')
            return

        #if sketch is None:
        sketch = self.Object.Sketch

        if sketch is None:
            print('Missing linked or local sketch')
            return

        return spline, sketch

    def _clear_loft(self):
        '''
        Delete the child objects in the loft group
        '''

        del_list = self.Object.OutList

        for obj in del_list:
            if obj.Label in ['sections', 'loft']:
                self.Object.removeObject(obj)

    def set_enabled(self, toggle):
        '''
        Enable the object for recomputation
        '''

        self.Enabled = toggle

    def set_stations(self, stations):
        '''
        Set the starting and ending station of the loft from the provided list
        '''

        pass

    def set_interval(self, interval):
        '''
        Set the section interval for the loft
        '''

        print('assigning interval ', interval)
        self.Object.Interval = interval
        print('interval assigned ', self.Object.Interval)

    def set_material(self, material):
        '''
        Set the name of the material for the loft
        '''

        pass

    def execute(self, obj):
        '''
        Rebuild the loft
        '''

        print('---> Execute.  Enabled? ', self.Enabled)
        if not self.Enabled:
            return

        self.Enabled = False
        self.regenerate()
        self.Enabled = True

    def _rebuild_geometry(self, generate_new):
        '''
        Retrieve existing geometry if found, otherwise create new
        '''

        loft_object = None

        for obj in self.Object.Group:

            print(obj.Label, obj.TypeId, obj.Name)
            if obj.Label == 'Loft':
                loft_object = obj
                break

        #if the loft object is not found and we're regenerating existing objects only, abort
        if loft_object:
            return loft_object

        if not generate_new:
            return None

        #    print ('-Removing ', loft_object.Name)
        #    self.Object.removeObject(loft_object)

        print('+new object in ', self.Object.Name)
        loft_object = self.Object.newObject('Part::Loft', 'Loft')
        loft_object.Label = 'Loft'

        print('++added new object ', loft_object.Name)
        return loft_object #, section_object

    def generate(self):
        '''
        Convenience function to force regeneration without existing geometry
        '''

        self.regenerate(True)

    def regenerate(self, generate_new=False):

        loft_object = self._rebuild_geometry(generate_new)

        if loft_object is None:
            return

        #get the support objects.  local copies supersede linked objects
        spline, sketch = self._get_support()

        #create loft sections
        section_list = self._build_sections(spline, sketch)

        print('generated ', len(section_list), ' sections...')
        #create a compound of the components (polygons)
        #section_object.Shape = Part.Compound(section_list)

        #loft the polygons to generate the solid
        #loft_object.Sections = section_object.Shape
        loft_object.Shape = Part.makeLoft(section_list, False, True, False)

        #self.Object.addObject(loft_object)

    def onChanged(self, obj, prop):
        print('onChanged ', prop)

    def onBeforeChange(self, obj, prop):
        print('onBeforeChange ', prop)

class _ViewProviderLoftGroup(object):

    def getIcon(self):
        return ''

    def __init__(self,vobj):
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self,vobj):
        print("attach " + str(vobj.Object.Label))
        self.Object = vobj.Object
        self.obj2=self.Object

        if not hasattr(self.Object,"Lock"):
                self.Object.Proxy.Lock=False

        App.ty=self
        App.tv=vobj

        return

    def claimChildren(self):
        return self.Object.Group

    def __getstate__(self):
        print("getstate " + str(self))
        return None

    def __setstate__(self,state):
        print("setstate " + str(self) + str(state))
        return None

    def setEdit(self,vobj,mode=0):
        return True

    def unsetEdit(self,vobj,mode=0):
        return False

    def doubleClicked(self,vobj):
        pass

    def setupContextMenu(self, obj, menu):
        pass
        #action = menu.addAction("About Transform")
        #action.triggered.connect(self.showVersion)

        #action = menu.addAction("Edit ...")
        #action.triggered.connect(self.edit)

    def edit(self):
        pass
        #self.dialog=TransformWidget(self)
        #self.dialog.show()

    def showVersion(self):
        pass
        #QtGui.QMessageBox.information(None, "About Transform", "Transform Node\n2015 microelly\nVersion " + __vers__ +"\nstill very alpha")
