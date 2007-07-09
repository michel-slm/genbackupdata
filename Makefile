all:

check:
	python-coverage -e
	python-coverage -x tests.py
	python-coverage -r -m -o /usr,/var | \
	    awk '{ print } /^TOTAL/ && $$2 != $$3 {exit 1}'
