all:

check:
	python -m CoverageTestRunner --ignore-missing-from without-tests
	./blackboxtest

clean:
	rm -rf *.py[co] */*.py[co] build dist MANIFEST 
	rm -f blackboxtest.log blackboxtest-genbackupdata.log

