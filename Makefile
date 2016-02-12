all: genbackupdata.1 manual.pdf manual.html

genbackupdata.1: genbackupdata.1.in genbackupdata
	./genbackupdata --generate-manpage=genbackupdata.1.in > genbackupdata.1

manual.pdf:
	pandoc -o manual.pdf manual.yarn

manual.html:
	pandoc -o manual.html --standalone manual.yarn
