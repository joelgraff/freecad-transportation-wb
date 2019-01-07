import FreeCAD 
app=FreeCAD
import FreeCADGui 
Gui=FreeCADGui

import PySide
from PySide import  QtGui,QtCore

import Draft
import FreeCAD as App


def combineCurves():


    #get selected horizontal and vertical geometry
    (h,v)=Gui.Selection.getSelection()

    #get list of geometry edges
    horiz_edge=h.Shape.Edges[0]
    vert_edge=v.Shape.Edges[0]

    #get the horizontal curve's first and last parameters
    fip=horiz_edge.FirstParameter
    lap=horiz_edge.LastParameter


    #get the length of the curve and set the step interval
    horiz_len=horiz_edge.Length
    step=3000

    #initialize point lists
    #ptsh is ... ?
    pts=[]
    ptsh=[FreeCAD.Vector(),FreeCAD.Vector(horiz_len,0,0),FreeCAD.Vector()]
    ptsn=[]
    ptsc=[]

    #divide the length by the number of steps, truncating the integer
    #then add one for the concluding point for the steps,
    #plus a point for the end of the edge, if the step point falls short
    point_count=int(horiz_len/float(step))+1

    if ((point_count - 1) * step) < horiz_len:
        point_count += 1

    #vertial curve as equidistant points at the step interval...
    vt_seg_pts=vert_edge.discretize(Number=point_count, First=0.00, Last=horiz_len)

    end_point = vt_seg_pts[point_count - 1]

    print('Start point: ',vt_seg_pts[0])
    print('End point: ',vt_seg_pts[point_count-1])

#c=FreeCAD.getDocument("stationing").getObject("MyBezierSketch")
#pts=c.Shape.Edge1.discretize(20)

    import numpy as np

    #this pairs coordinates of like axes in three tuples (x_coords,y_coords,z)
    vt_pt_seg_axes=np.array(vt_seg_pts).swapaxes(0,1)

    #save the x_coords/y_coords coordinate pairs in separate variables
    x_coords=list(range(0, int(horiz_len) + 1, step))

    #if we added two to the point count, then the step interval
    #won't quite make it to the end... add the length as the last point
    if len(x_coords) < point_count:
        x_coords.append(horiz_len)

    last_pt = len(x_coords)
    print(x_coords[last_pt - 10:])

    y_coords=vt_pt_seg_axes[1]

    #append the final elevation - see above
    if (len(y_coords) < point_count):
        y_coords = np.append(y_coords, end_point.y)

    print(len(x_coords))
    print(len(y_coords))

    #interpolation...
    from scipy import interpolate
    ff = interpolate.interp1d(x_coords, y_coords,kind='cubic',bounds_error=False,fill_value=0)

    ll = int(h.Shape.Length) + 1

    #create a set of x_coords-values evenly spaced between 0 and ll at the specified step interval
    xnew=np.arange(0,ll,step)

    last_element = xnew[len(xnew)-1]

    if last_element != h.Shape.Length:
        xnew = np.append(xnew, h.Shape.Length)

    #interpolates y_coords values for the specified x_coords values
    ynew = ff(xnew)   # use interpolation function returned by `interp1d`


        #ynew = np.append(ynew, vert_edge.Curve.parameterAtDistance(horiz_len))
#	plt.plot(x_coords, y_coords, 'o', xnew, ynew, '+')
#	plt.show()

    #minimum of point_count, and the number of intervals in xnew
    #anz2=min(point_count,xnew.shape[0])

    print ('point_count: ', point_count)
    print ('xnew.shape[0]', xnew.shape[0])
    #print ("anz2: ", anz2)

    for i in range(xnew.shape[0]):

        print(xnew[i], ynew[i])
        #x,y coordinate on horizontal
        #p=horiz_edge.valueAt(fip+step*(lap-fip)/horiz_len*i)

        #tangent at point
        t=horiz_edge.tangentAt(fip+step*(lap-fip)/horiz_len*i)

        #x,y coordinate on horizontal
        p=horiz_edge.Curve.value(fip+step*(lap-fip)/horiz_len*i)


        #stationing line interval
        f=2
        if  i%5 == 0:
            f=4
        if  i%10 == 0:
            f=10
        if  i%50 == 0:
            f=30

        #calculate normal vector at point
        n=f*t.cross(FreeCAD.Vector(0,0,1))
        
        #hp=FreeCAD.Vector(p.x_coords,p.y_coords,hz_seg_pts[i].y_coords)
        # print i

        #generate z-coordinate for 3D spline
        hp=FreeCAD.Vector(p.x,p.y,ynew[i])
        
        pts += [p,p+n,p,p-n,p]
        ptsn += [p,hp,p]
        
        hh=FreeCAD.Vector(xnew[i],ynew[i],0)
        vpp = vert_edge.Curve.parameterAtDistance(xnew[i])
        #vpp=vert_edge.Curve.parameter(hh)
        vtt=vert_edge.tangentAt(vpp)
        vn=f*vtt.cross(FreeCAD.Vector(0,0,1))
        
        #ptsh += [hz_seg_pts[i],hz_seg_pts[i]+vn,hz_seg_pts[i]-vn,hz_seg_pts[i]]
        ptsh += [hh,hh+vn,hh-vn,hh]
        
        ptsc += [hp]

    import Part

    #stationing along horizontal curve
    res=App.ActiveDocument.getObject("Wxy")
    if res == None:
        res=App.activeDocument().addObject('Part::Feature','Wxy')

    res.Shape=Part.makePolygon(pts)

    #
    res=App.ActiveDocument.getObject("Whmap")
    if res == None:
        res=App.activeDocument().addObject('Part::Feature','Whmap')

    res.Shape=Part.makePolygon(ptsn)

    #station along vertical curve
    res=App.ActiveDocument.getObject("Wh")
    if res == None:
        res=App.activeDocument().addObject('Part::Feature','Wh')

    res.Shape=Part.makePolygon(ptsh)
    
    res=App.ActiveDocument.getObject("W3D")
    if res == None:
        res=App.activeDocument().addObject('Part::Feature','W3D')

    s=Part.BSplineCurve()
    s.interpolate(ptsc)
    
    res.Shape=s.toShape()



