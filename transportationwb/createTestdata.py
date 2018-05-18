'''create some real environments with hard coded coordinates

these scripts use the geodat workbench.
'''

def createEichleite():
	'''Wilhelmsthal Eichleite Friesener Berg steiler kurviger Anstieg 50.2725064,11.3946793'''
	import geodat
	from geodat import import_osm

	bk=0.5
	b,l = 50.2725064,11.3946793

	progressbar=False
	status=False
	elevation=False

	if not geodat.import_osm.import_osm2(b,l,bk,progressbar,status,elevation):
		geodat.import_osm.import_osm2(b,l,bk,progressbar,status,elevation)


def createWoosung():
	'''testcase by Joel 41.8846258,-89.5806548'''
	import geodat
	from geodat import import_osm

	bk=2
	b,l = 41.8846258,-89.5806548

	progressbar=False
	status=False
	elevation=False

	if not geodat.import_osm.import_osm2(b,l,bk,progressbar,status,elevation):
		geodat.import_osm.import_osm2(b,l,bk,progressbar,status,elevation)



def createJapaneseKnot():
	'''complex highway crossing 35.624446,139.263'''

	import geodat
	from geodat import import_osm

	bk=0.5
	b,l = 35.624446,139.263

	progressbar=False
	status=False
	elevation=False

	if not geodat.import_osm.import_osm2(b,l,bk,progressbar,status,elevation):
		geodat.import_osm.import_osm2(b,l,bk,progressbar,status,elevation)
