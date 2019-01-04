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
    step=3.

    #initialize point lists
    #ptsh is ... ?
    pts=[]
    ptsh=[FreeCAD.Vector(),FreeCAD.Vector(horiz_len,0,0),FreeCAD.Vector()]
    ptsn=[]
    ptsc=[]

    #divide the length by the number of steps and add one, rounding up
    #to give the segment length
    seg_len=int(round(horiz_len/step)+1)

    #horizontal curve as equidistant points at the step interval...
    hz_seg_pts=vert_edge.discretize(seg_len)


#c=FreeCAD.getDocument("stationing").getObject("MyBezierSketch")
#pts=c.Shape.Edge1.discretize(20)

    import numpy as np

    #this pairs coordinates of like axes in three tuples (x_coords,y_coords,z)
    hz_pt_seg_axes=np.array(hz_seg_pts).swapaxes(0,1)

    #save the x_coords/y_coords coordinate pairs in separate variables
    x_coords=hz_pt_seg_axes[0]
    y_coords=hz_pt_seg_axes[1]

    #interpolation...
    from scipy import interpolate
    ff = interpolate.interp1d(x_coords, y_coords,kind='cubic',bounds_error=False,fill_value=0)

    #ll=800
    #st=int(round(ll/seg_len))

    #ll is an upper limit
    ll=int(round(seg_len*step+1))
    # ll=800

    #create a set of x_coords-values evenly spaced between 0 and ll at the specified step interval
    xnew=np.arange(0,ll,int(step))

#	print ("!!gefuden", seg_len,xnew.shape,ll)
#	print ("xdims",x_coords.max(),	x_coords.min())
#	print ("xnewdims",xnew.max(),	xnew.min())

#	print xnew

    #interpolates y_coords values for the specified x_coords values
    ynew = ff(xnew)   # use interpolation function returned by `interp1d`

#	plt.plot(x_coords, y_coords, 'o', xnew, ynew, '+')
#	plt.show()

    #minimum of seg_len, and the number of intervals in xnew
    anz2=min(seg_len,xnew.shape[0])

    for i in range(anz2):

        
        p=horiz_edge.valueAt(fip+step*(lap-fip)/horiz_len*i)

        t=horiz_edge.tangentAt(fip+step*(lap-fip)/horiz_len*i)

        p=horiz_edge.Curve.value(fip+step*(lap-fip)/horiz_len*i)
        
        f=2
        if  i%5 == 0:
            f=4
        if  i%10 == 0:
            f=10
        if  i%50 == 0:
            f=30

        n=f*t.cross(FreeCAD.Vector(0,0,1))
        
        #hp=FreeCAD.Vector(p.x_coords,p.y_coords,hz_seg_pts[i].y_coords)
        # print i

        hp=FreeCAD.Vector(p.x_coords,p.y_coords,ynew[i])
        
        pts += [p,p+n,p,p-n,p]
        ptsn += [p,hp,p]
        
        hh=FreeCAD.Vector(xnew[i],ynew[i],0)
        vpp=vert_edge.Curve.parameter(hh)
        vtt=vert_edge.tangentAt(vpp)
        vn=f*vtt.cross(FreeCAD.Vector(0,0,1))
        
        #ptsh += [hz_seg_pts[i],hz_seg_pts[i]+vn,hz_seg_pts[i]-vn,hz_seg_pts[i]]
        ptsh += [hh,hh+vn,hh-vn,hh]
        
        ptsc += [hp]

    import Part

    res=App.ActiveDocument.getObject("Wxy")
    if res == None:
        res=App.activeDocument().addObject('Part::Feature','Wxy')

    res.Shape=Part.makePolygon(pts)

    res=App.ActiveDocument.getObject("Whmap")
    if res == None:
        res=App.activeDocument().addObject('Part::Feature','Whmap')

    res.Shape=Part.makePolygon(ptsn)


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



