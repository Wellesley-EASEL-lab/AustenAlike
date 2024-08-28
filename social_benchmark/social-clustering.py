import csv
import sys
from random import shuffle
from sklearn.cluster import KMeans
from sklearn import metrics
import numpy as np
"""
Script for analyzing similarity by narratological role
"""

def avg_vector(embeds):
	return np.mean(list(embeds.values()),axis=0)


def norm_data(data,norm):
	for k,v in data.items():
		data[k] = [v[i]-norm[i] for i in range(len(norm))]


def read_character_data(f):
	data = {}
	with open(f,'r') as of:
		reader = csv.reader(of,delimiter="\t")
		for line in reader:
			character = line[1]
			data[character] = [float(i) for i in line[2:]]
		return data

def read_benchmark_data(char_map,data): 
	benchmark = {}
	with open("austen-social.tsv",'r') as of:
		reader = csv.DictReader(of,delimiter='\t')
		for line in reader:
			char = char_map[line['name']]
			if char not in data:
				print("Missing",char)
			for cat in ['startIncome','endIncome','gender','age','estAge','rank','maritalStatus']:
				val = line[cat]
				if (cat,val) not in benchmark:
					benchmark[(cat,val)] = [char]
				else:
					benchmark[(cat,val)].append(char)
		benchmark_age = bin_age(benchmark)
		for k,v in benchmark_age.items():
			benchmark[("Age",k)] = v
		to_remove = [k for k in benchmark if 'estAge' in k or 'age' in k]
		benchmark_income = bin_income(benchmark)
		for k,v in benchmark_income.items():
			benchmark[("Income",k)] = v
		to_remove += [k for k in benchmark if 'startIncome' in k or 'endIncome' in k]
		for k in to_remove:
			del benchmark[k]

	return benchmark

def find_age_bin(age,bins):
	for i in bins:
		if i >= age:
			return i

def bin_age(data):
	bins = [17,20,24,27,30,40,50,60]
	ageDict = {k:[] for k in bins}
	all_ages = []
	all_est_ages = []
	ages = dict([(k[1],v) for k,v in data.items() if k[0] == 'age'])
	estAges = dict([(k[1],v) for k,v in data.items() if k[0] == 'estAge'])
	for k,v in ages.items():
		all_ages += [(int(k),i) for i in v if k.strip()]
	for k,v in estAges.items():
		all_est_ages += [(int(k),i) for i in v]
	age_pairs = all_ages + [(k,v) for k,v in all_est_ages if v not in [z[1] for z in all_ages]]
	for age,char in age_pairs:
		ageDict[find_age_bin(age,bins)].append(char)
	return ageDict

def find_income_bin(income,bins):
	for i in bins:
		if i >= income:
			return i

def bin_income(data):
	startIncome = dict([(k[1],v) for k,v in data.items() if k[0] == 'startIncome'])
	endIncome = dict([(k[1],v) for k,v in data.items() if k[0] == 'endIncome'])
	all_starts = {}
	all_ends = {}
	bins = [50,250,500,1000,3000,15000]
	incomeDict = {k:[] for k in bins}
	for k,v in startIncome.items():
		if k:
			for char in v:
				all_starts[char] = int(k)
	for k,v in endIncome.items():
		if k:
			for char in v:
				if char not in all_starts:
					all_starts[char] = int(k)
	for char,income in all_starts.items():
		incomeDict[find_income_bin(income,bins)].append(char)
	return incomeDict


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
				print(k,"missing",char)
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
		print(len(ingroup))
		for i in range(50):
			shuffle(data)
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
		of.write("Dataset,Category,Group,InGroupSize,Run,Purity\n")
		for k,v in purity_dict.items():
			for i,score in enumerate(v):
				group,size = k
				of.write(f"{tag},{k[0]},{k[1]},{size},{i},{score}\n")

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
