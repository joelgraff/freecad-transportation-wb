import FreeCAD 
app=FreeCAD
import FreeCADGui 
Gui=FreeCADGui

import PySide
from PySide import  QtGui,QtCore

import Draft
import FreeCAD as App


def combineCurves():


	(h,v)=Gui.Selection.getSelection()

	hw=h.Shape.Edges[0]
	vw=v.Shape.Edges[0]


	fip=hw.FirstParameter
	lap=hw.LastParameter



	l=hw.Length
	step=3.

	pts=[]
	ptsh=[FreeCAD.Vector(),FreeCAD.Vector(l,0,0),FreeCAD.Vector()]
	ptsn=[]
	ptsc=[]

	anz=int(round(l/step)+1)

	hps=vw.discretize(anz)


#c=FreeCAD.getDocument("stationing").getObject("MyBezierSketch")
#pts=c.Shape.Edge1.discretize(20)

	import numpy as np

	hhps=np.array(hps).swapaxes(0,1)

	x=hhps[0]
	
	y=hhps[1]

	from scipy import interpolate
	ff = interpolate.interp1d(x, y,kind='cubic',bounds_error=False,fill_value=0)

	#ll=800
	#st=int(round(ll/anz))
	ll=int(round(anz*step+1))
	# ll=800
	xnew=np.arange(0,ll,int(step))
#	print ("!!gefuden", anz,xnew.shape,ll)
#	print ("xdims",x.max(),	x.min())
#	print ("xnewdims",xnew.max(),	xnew.min())

#	print xnew
	ynew = ff(xnew)   # use interpolation function returned by `interp1d`
#	plt.plot(x, y, 'o', xnew, ynew, '+')
#	plt.show()

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



