import csv

with open("austen-pairs.tsv",'r') as of:
	d = {}
	reader = csv.reader(of,delimiter="\t")
	lines = [l for l in reader]

m = {}
with open('../character_map.tsv','r') as of:
	reader = csv.reader(of,delimiter="\t")
	for line in reader:
		book = line[0]
		alias = line[1]
		name = line[2]
		m[alias] = name
for i,line in enumerate(lines):
	name2 = line[1]
	name = line[0]
	if name not in m:
		print(i,[name])
	if name2 not in m:
		print(i,[name2])



