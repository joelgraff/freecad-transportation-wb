gendoc:

pep:
	#autopep8 --ignore=W191,E101,E111 miki_g.py >t.py
	#pylint -E miki_g.py
	pylint miki_g.py

gendoc:
	doxygen


genlog:
	echo 'date="' `date`  '"' >>__init__.py
	echo 'version='`git rev-list --all --count` >>__init__.py

