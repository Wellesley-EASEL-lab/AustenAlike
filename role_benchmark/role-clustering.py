import csv
import sys
from sklearn.cluster import KMeans
from sklearn import metrics
from random import shuffle
import numpy as np
"""
Script for analyzing similarity by narratological role
"""

def avg_vector(embeds):
	return np.mean(list(embeds.values()),axis=0)


def norm_data(data,norm):
	for k,v in data.items():
		data[k] = [v[i]-norm[i] for i in range(len(norm))]


def read_benchmark_data(char_map,data): 
	benchmark = {}
	with open("austen-roles.tsv",'r') as of:
		reader = csv.reader(of,delimiter='\t')
		for char,novel,role in reader:
			char = char_map[char]
			if char not in data:
				print("Missing",char)
			if role not in benchmark:
				benchmark[role] = [char]
			else:
				benchmark[role].append(char)
	return benchmark

def read_character_list():
	novel_map = {}
	with open("../austen-novels.tsv",'r') as of:
		reader = csv.reader(of,delimiter='\t')
		for char,novel in reader:
			novel_map[char] = novel
	return novel_map

def read_char_map():
	m = {}
	with open("../character_map.tsv",'r') as of:
		reader = csv.reader(of,delimiter="\t")
		for line in reader:
			book = line[0]
			alias = line[1]
			name = line[2]
			m[alias] = name
	return m

def read_character_data(f):
	data = {}
	with open(f,'r') as of:
		reader = csv.reader(of,delimiter="\t")
		for line in reader:
			character = line[1]
			data[character] = [float(i) for i in line[2:]]
		return data

def make_clustering_data(data,benchmark):
	pairs = []
	label_map = {}
	for k, v in benchmark.items():
		if k not in label_map:
			label_map[k] = len(label_map)
		lab = label_map[k]
		for char in v:
			if char in data:
				pairs.append((data[char],lab))
			else:
				print(char)
	shuffle(pairs)
	return pairs,label_map


def clustering_analysis(data,benchmark,novel_map):
	pairs,label_map = make_clustering_data(data,benchmark)
	purity_dict = {}
	for k,v in label_map.items():
		purities = []
		ingroup = [(x,1) for x,y in pairs if y==v]
		outgroup = [(x,0) for x,y in pairs if y!=v]
		data = ingroup+outgroup
		shuffle(data)
		for i in range(len(data)):
			include = data[:i]+data[i+1:]
			x = [x for x,y in include]
			y = [y for x,y in include]
			model = KMeans(init="k-means++", n_clusters=2, n_init=75, random_state=0)
			kmeans = model.fit(x)
			purity = metrics.adjusted_rand_score(y,kmeans.labels_)
			purities.append(purity)
		ap = sum(purities)/len(purities)
		print("Category",k,"average purity:",ap)
		print("Category",k,"size-corrected average purity:",ap/len(ingroup))
		purity_dict[(k,len(ingroup))] = purities
	return purity_dict

def export(purity_dict,tag):
	with open(f"results/{tag}_clusters.csv",'w') as of:
		of.write("Dataset,Category,InGroupSize,Run,Purity\n")
		for k,v in purity_dict.items():
			for i,score in enumerate(v):
				group,size = k
				of.write(f"{tag},{group},{size},{i},{score}\n")


def main():
	f = sys.argv[1]
	tag = sys.argv[2]
	scale = sys.argv[3]
	novel_map = read_character_list()
	char_map = read_char_map()
	data = read_character_data(f)
	if scale == "scale":
		norm = avg_vector(data)
		norm_data(data,norm)
	benchmark = read_benchmark_data(char_map,data)
	purity_dict = clustering_analysis(data,benchmark,novel_map)
	export(purity_dict,tag)


main()