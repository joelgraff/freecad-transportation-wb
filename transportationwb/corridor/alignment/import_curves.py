import FreeCAD as App
import Draft
import os
import json
from PySide import QtGui
from PySide import QtCore

def f_x(a, b, c, x):

    return a * x * x + b * x + c

def build_vertical_element(e):

    a = (e["g2"] - e["g1"]) /  (2 * e["length"])
    points = []

    x = 0.0
    incr = e["length"] / 5.0

    for i in range (0, 5):
        points.append(App.Vector(x, f_x(a, e["g1"], e["elevation"], x), 0.0))
        x += incr
    
    print(points)
    return points

def build_vertical_spline(elements):

    points = []

    for _e in elements:
        _e["elevation"] -= (_e["g1"] * (_e["length"] / 2.0))
        points.extend(build_vertical_element(_e))

    spline = App.ActiveDocument.addObject("Part::Part2DObjectPython", "BSpline")

    Draft._BSpline(spline)
    spline.Closed = False
    spline.Points = points
    spline.Support = None
    spline.Label = "test_alignment"

    Draft._ViewProviderWire(spline.ViewObject)

    return spline

def _dms_to_deg (deg, mins, sec):

    return float(deg) + (float(mins) / 60.0) + (float(sec) / 60.0)

def getFile():
    '''
    Displays the file browser dialog to pick the JSON file
    '''
    dlg = QtGui.QFileDialog()
    options = dlg.Options()
    options |= dlg.DontUseNativeDialog
    dlg.setDefaultSuffix('.json')
    file_name, _ = dlg.getOpenFileName(dlg,"QFileDialog.getOpenFileName()", "","All Files (*);;JSON Files (*.json)", options=options)

    return os.path.split(file_name)

def convert_horizontal_csv(): #path, infile, outfile):
    data_set = []
    meta = {}
    geometry = []
    bearing = []
    tangent = []
    bearing_quad = ''

    file_path = getFile()

    if file_path == '':
        return

    data = None

    out_file = file_path[0] + '/' + file_path[1].split('.')[0] + '.json'

    csv = open(file_path[0] + '/' + file_path[1], 'r')

    lines = csv.read().splitlines()

    csv.close()

    for line in lines:

        tokens = list(filter(None, line.split(',')))

        if tokens[0] == 'id':

            if meta:

                if bearing:
                    meta['limits'].append(tangent[0] + tangent[1])

                data_set.append({'meta': meta, 'geometry': geometry})

                geometry = []
                bearing = []
                tangent = []

            meta = {'id': tokens[1], 'units': 'english', 'st_eq': [], 'location':[], 'limits':[], 'bearing':[], 'quadrant':''}

        elif tokens[0] == 'sta_eq':
            meta['st_eq'].append(tokens[1:3])

        elif tokens[0] == 'location':
            meta['location'].extend(tokens[1:4])

        elif tokens[2] in ['NE', 'NW', 'SE', 'SW']:
            bearing = [float(tokens[3]), float(tokens[4]), float(tokens[5])]
            bearing_quad = tokens[2]
            tangent = [float(tokens[0]), float(tokens[1])]

            if not meta['limits']:
                meta['limits'].append(float(tokens[0]))
                meta['bearing'].extend(bearing)
                meta['quadrant'] = tokens[2]

        elif tokens[2] in ['L', 'R']:
            geometry.append({
                'PC_station': tokens[0],
                'bearing': bearing,
                'quadrant': bearing_quad,
                'direction': tokens[2],
                'radius': tokens[1],
                'central_angle': [float(tokens[3]), float(tokens[4]), float(tokens[5])]
            })

            if not meta['limits']:
                meta['limits'].append(float(tokens[0]))

            bearing = []
            tangent = []

    if bearing:
        meta['limits'].append(tangent[0] + tangent[1])

    data_set.append({'meta': meta, 'geometry': geometry})

    jsn = open(out_file, 'w')
    json.dump(data_set, jsn)
    jsn.close()

    return data_set

def convert_vertical_csv(path, infile, outfile):

    data_set = []
    alignment = {}
    geometry = []
    csv = open(path + '/' + infile, 'r')

    lines = csv.read().splitlines()

    csv.close()

    for line in lines:

        tokens = list(filter(None, line.split(',')))
        count = len(tokens)
        
        #encountered id of new alignment.  Save existing data and reset
        if count == 1:

            if alignment:
                data_set.append({'meta': alignment, 'geometry': geometry})
                geometry = []

            alignment = {'id': tokens[0], 'units': 'english', 'st_eq': [] }

        elif count == 2:
            alignment['st_eq'].append(tokens)

        elif count == 4:

            geometry.append({
                'pi': tokens[0],
                'elevation': tokens[1],
                'g1': tokens[2],
                'g2': tokens[3]
            })

        elif count == 5:
            geometry.append({
                'pi': tokens[0],
                'length': tokens[1],
                'elevation': tokens[2],
                'g1': tokens[3],
                'g2': tokens[4]
            })

    data_set.append({'alignment': alignment, 'geometry': geometry})

    jsn = open(path + '/' + outfile, 'w')
    json.dump(data_set, jsn)
    jsn.close()

    return data_set