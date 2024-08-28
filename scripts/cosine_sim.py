import sys
import csv
from sklearn.metrics.pairwise import cosine_similarity

"""
Script for calculating cosine similarity between all pairs of characters in Austen from mega representations
"""

def read_data(f):
	data = {}
	with open(f,'r') as of:
		reader = csv.reader(of,delimiter="\t")
		for line in reader:
			data[line[1]] = [float(i) for i in line[2:]]
	return data

def cosine_sim(x,y):
	return round(cosine_similarity([x],[y])[0][0],6)

def filter_data(data,novel_map):
	remove = []
	for k in novel_map:
		if k not in data:
			print("Missing",k)
	for k in data:
		if k not in novel_map:
			print(k)
			remove.append(k)
	for k in remove:
		del data[k]

def find_all_pairs(data):
	sims = {}
	for k,v in data.items():
		for j,w in data.items():
			sim = cosine_sim(v,w)
			if k not in sims:
				sims[k] = {j:sim}
			else:
				sims[k][j] = sim
	return sims

def read_character_list():
	novel_map = {}
	with open("../austen-novels.tsv",'r') as of:
		reader = csv.reader(of,delimiter='\t')
		for char,novel in reader:
			novel_map[char] = novel
	return novel_map

def export(data,outf):
	with open(outf,'w') as of:
		writer = csv.writer(of)
		header = sorted(data.keys())
		writer.writerow(['character']+header)
		for k,v in sorted(data.items()):
			assert([i for i,sim in sorted(v.items())]==header)
			line = [k] + [sim for i,sim in sorted(v.items())]
			writer.writerow(line)

def main():
	f = sys.argv[1]
	outf = sys.argv[2]
	data = read_data(f)
	novel_map = read_character_list()
	filter_data(data,novel_map)
	sims = find_all_pairs(data)
	export(sims,outf)


main()