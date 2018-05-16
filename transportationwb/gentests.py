#create testcases from source file

head='''
class {}_Test(unittest.TestCase):

	def setUp(self):

		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "TransportationTest":
				FreeCAD.newDocument("TransportationTest")
		else:
			FreeCAD.newDocument("TransportationTest")
		FreeCAD.setActiveDocument("TransportationTest")

'''

foot='''
	def tearDown(self):
		FreeCAD.closeDocument("TransportationTest")
'''

def run(out,ifn,fn):
		print (ifn,fn)
		import re

		res = re.search(r".*/(\S+)\.py", fn)
		modul='clipplane'
		modul=res.group(1)
#		print modul
		out.write(head.format(modul))

		fp=open(fn)
		anz=0
		for i,line in enumerate(fp):
			if line.startswith('def'):
				res = re.search(r"def\s+(\S+)\((.*)\):\s*", line)
				if res:
						anz +=1
						fun=res.group(1)
						args=res.group(2)
						print ("    ",anz,fun,args)
						out.write( "	def test_"+fun+"(self):\n")
						out.write("\n" )
						out.write("		import transportationwb."+modul+"\n")
						out.write("		reload (transportationwb."+modul+")\n")
						out.write("		rc=transportationwb."+modul+"."+fun+"("+args+")\n")
						out.write("\n")
		out.write(foot)
		return anz


def runall(fns):
	out=open('/home/thomas/.FreeCAD/Mod/freecad-transportation-wb/transportationwb/Test_top_generated.py', 'w')
	out.write('''import FreeCAD\nimport unittest\n''')

	anzsum=0
	for i,fn in enumerate(fns):
		anzsum += run(out,i,fn)
	print ("gesamt",anzsum)


#-----------------------------


t='''beziersketch.py
bogen_zeichnen.py
clipplane.py
create_circle_sketch.py
geodesic_lines.py
labeltools.py
miki_g.py
mydoxypy.py
say.py
stationing.py
transversmercator.py
'''

fns=['/home/thomas/.FreeCAD/Mod/freecad-transportation-wb/transportationwb/'+l for l in t.splitlines()]

runall(fns)
