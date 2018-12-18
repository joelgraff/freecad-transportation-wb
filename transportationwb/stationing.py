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
	hw=h.Shape.Edges[0]
	vw=v.Shape.Edges[0]

	#get the horizontal curve's first and last parameters
	fip=hw.FirstParameter
	lap=hw.LastParameter


	#get the length of the curve and set the step interval
	l=hw.Length
	step=3.

	#initialize point lists
	#ptsh is ... ?
	pts=[]
	ptsh=[FreeCAD.Vector(),FreeCAD.Vector(l,0,0),FreeCAD.Vector()]
	ptsn=[]
	ptsc=[]

	#inverse step... ceiling + 1?
	anz=int(round(l/step)+1)

	#horizontal curve as equidistant points at the step interval...
	hps=vw.discretize(anz)


#c=FreeCAD.getDocument("stationing").getObject("MyBezierSketch")
#pts=c.Shape.Edge1.discretize(20)

	import numpy as np

	#this pairs coordinates of like axes in three tuples (x,y,z)
	hhps=np.array(hps).swapaxes(0,1)

	#save the x/y coordinate pairs in separate variables
	x=hhps[0]
	y=hhps[1]

	#interpolation...
	from scipy import interpolate
	ff = interpolate.interp1d(x, y,kind='cubic',bounds_error=False,fill_value=0)

	#ll=800
	#st=int(round(ll/anz))

	#ll is an upper limit
	ll=int(round(anz*step+1))
	# ll=800

	#create a set of x-values evenly spaced between 0 and ll at the specified step interval
	xnew=np.arange(0,ll,int(step))

#	print ("!!gefuden", anz,xnew.shape,ll)
#	print ("xdims",x.max(),	x.min())
#	print ("xnewdims",xnew.max(),	xnew.min())

#	print xnew

	#interpolates y values for the specified x values
	ynew = ff(xnew)   # use interpolation function returned by `interp1d`

#	plt.plot(x, y, 'o', xnew, ynew, '+')
#	plt.show()

	#minimum of anz, and the number of intervals in xnew
	anz2=min(anz,xnew.shape[0])

	for i in range(anz2):

		
		p=hw.valueAt(fip+step*(lap-fip)/l*i)

		t=hw.tangentAt(fip+step*(lap-fip)/l*i)

		p=hw.Curve.value(fip+step*(lap-fip)/l*i)
		
		f=2
		if  i%5 == 0:
			f=4
		if  i%10 == 0:
			f=10
		if  i%50 == 0:
			f=30

		n=f*t.cross(FreeCAD.Vector(0,0,1))
		
		#hp=FreeCAD.Vector(p.x,p.y,hps[i].y)
		# print i

		hp=FreeCAD.Vector(p.x,p.y,ynew[i])
		
		pts += [p,p+n,p,p-n,p]
		ptsn += [p,hp,p]
		
		hh=FreeCAD.Vector(xnew[i],ynew[i],0)
		vpp=vw.Curve.parameter(hh)
		vtt=vw.tangentAt(vpp)
		vn=f*vtt.cross(FreeCAD.Vector(0,0,1))
		
		#ptsh += [hps[i],hps[i]+vn,hps[i]-vn,hps[i]]
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



