all: genbackupdata.1

genbackupdata.1: genbackupdata.1.in genbackupdata
	./genbackupdata --generate-manpage=genbackupdata.1.in > genbackupdata.1

check:
	python -m CoverageTestRunner --ignore-missing-from without-tests
	./blackboxtest

clean:
	rm -rf *.py[co] */*.py[co] build dist MANIFEST 
	rm -f blackboxtest.log blackboxtest-genbackupdata.log

