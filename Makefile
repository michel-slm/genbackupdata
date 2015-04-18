all: genbackupdata.1

genbackupdata.1: genbackupdata.1.in genbackupdata
	./genbackupdata --generate-manpage=genbackupdata.1.in > genbackupdata.1

check:
	python -m CoverageTestRunner --ignore-missing-from without-tests
	rm -f .coverage
	cmdtest tests
	pep8 genbackupdata genbackupdatalib

clean:
	rm -rf *.py[co] */*.py[co] build dist MANIFEST 
	rm -f blackboxtest.log blackboxtest-genbackupdata.log
