import csv

with open("austen-novels.tsv",'r') as of:
	d = {}
	reader = csv.reader(of,delimiter="\t")
	lines = sorted([l for l in reader],key=lambda x:x[1])

with open('character_map.tsv','w') as of:
	for l in lines:
		of.write(f"{l[1]}\t{l[0]}\t{l[0]}\n")
		bits = l[0].split()
		if bits[0] not in ["Mr.","Mrs.","Miss","Lady","Sir","Admiral","Lieutenant","Dr."]:
			of.write(f"{l[1]}\t{bits[0]}\t{l[0]}\n")



