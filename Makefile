all:

check:
	python-coverage -e
	python-coverage -x tests.py
	python-coverage -r -m -o /usr,/var | \
	    awk '{ print } /^TOTAL/ && $$2 != $$3 {exit 1}'
	./blackboxtest

clean:
	rm -rf *.pyc *.pyo build dist MANIFEST 
	rm -f blackboxtest.log blackboxtest-genbackupdata.log

dist:
	python setup.py sdist
