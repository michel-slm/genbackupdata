all:

check:
	python -m CoverageTestRunner --ignore-missing-from without-tests
#	./blackboxtest

clean:
	rm -rf *.pyc *.pyo build dist MANIFEST 
	rm -f blackboxtest.log blackboxtest-genbackupdata.log

dist:
	python setup.py sdist
