all: genbackupdata.1

genbackupdata.1: genbackupdata.1.in genbackupdata
	./genbackupdata --generate-manpage=genbackupdata.1.in > genbackupdata.1
