import sys

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

ignore=True
with open(sys.argv[1]) as fp:
    for i,line in enumerate(fp):
		if not ignore:
			print line.rstrip()
		else:
			if not line.startswith('#'):
				print line.rstrip()
				ignore=False
