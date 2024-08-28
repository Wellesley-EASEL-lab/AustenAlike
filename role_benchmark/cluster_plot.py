import csv
import sys
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt 
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
plt.rcParams.update({'font.size': 14})

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
		reader = csv.reader(of)
		for line in reader:
			character = line[0]
			data[character] = [float(i) for i in line[1:]]
		return data

def make_clustering_data(data,benchmark):
	feats = []
	labs = []
	label_map = {}
	for k, v in benchmark.items():
		if k not in label_map:
			label_map[k] = len(label_map)
		lab = label_map[k]
		for char in v:
			if char in data:
				feats.append(data[char])
				labs.append((char,lab))
			else:
				print(char)
	return feats,labs,label_map

def cluster(feats,labs,label_map):
	scaler =StandardScaler()
	features = scaler.fit(feats)
	features = features.transform(feats)
	scaled_df =pd.DataFrame(features)
	X = scaled_df.values
	#kmeans = KMeans(n_clusters = 7, init = 'k-means++',n_init=75, random_state=0)
	#kmeans.fit(X)
	pca=PCA(n_components=2)
	reduced_X=pd.DataFrame(data=pca.fit_transform(X),columns=['PCA1','PCA2'])
	#centers=pca.transform(kmeans.cluster_centers_)
	
	fig = plt.figure(figsize=(7,5))
	# Scatter plot
	scatter = plt.scatter(reduced_X['PCA1'],reduced_X['PCA2'],c=[x[1] for x in labs],cmap="Dark2")
	#plt.scatter(centers[:,0],centers[:,1],marker='x',c='red')
	for i, txt in enumerate(labs):
		if txt[1] == -1:
			plt.annotate(txt[0], (reduced_X['PCA1'][i], reduced_X['PCA2'][i]))
	plt.xlabel('PCA1')
	plt.ylabel('PCA2')
	plt.title('FanfictionNLP Assertions')
	plt.tight_layout()
	plt.show()



def main():
	f = sys.argv[1]
	novel_map = read_character_list()
	char_map = read_char_map()
	data = read_character_data(f)
	benchmark = read_benchmark_data(char_map,data)
	feats,labs,label_map = make_clustering_data(data,benchmark)
	print(label_map)
	cluster(feats,labs,{v:k for k,v in label_map.items()})


main()