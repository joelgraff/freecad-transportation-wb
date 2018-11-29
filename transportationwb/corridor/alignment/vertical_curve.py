import FreeCAD as App
import Draft
import json

def f_x(a, b, c, x):

    return a * x * x + b * x + c

def build_element(e):

    a = (e["g2"] - e["g1"]) /  (2 * e["length"])
    points = []

    x = 0.0
    incr = e["length"] / 5.0

    for i in range (0, 5):
        points.append(App.Vector(x, f_x(a, e["g1"], e["elevation"], x), 0.0))
        x += incr
    
    print(points)
    return points

def build_spline(elements):

    points = []

    for _e in elements:
        _e["elevation"] -= (_e["g1"] * (_e["length"] / 2.0))
        points.extend(build_element(_e))

    spline = App.ActiveDocument.addObject("Part::Part2DObjectPython", "BSpline")

    Draft._BSpline(spline)
    spline.Closed = False
    spline.Points = points
    spline.Support = None
    spline.Label = "test_alignment"

    Draft._ViewProviderWire(spline.ViewObject)

    return spline

def convert_csv(path, infile, outfile):

    data = {'alignment': {'st_eq': []}, 'geometry': []}

    csv = open(path + '/' + infile, 'r')

    lines = csv.read().splitlines()

    csv.close()

    for line in lines:

        print(line)
        tokens = line.split(',')
        count = len(tokens)

        if count == 1:
            data['alignment']['id'] = tokens[0]

        elif count == 2:
            data['alignment']['st_eq'].append(tokens)

        elif count == 5:
            geo = {
                'pi': tokens[0],
                'length': tokens[1],
                'elevation': tokens[2],
                'g1': tokens[3],
                'g2': tokens[4]
            }
            data['geometry'].append(geo)
    
    jsn = open(path + '/' + outfile, 'w')
    json.dump(data, jsn)
    jsn.close()

    return data