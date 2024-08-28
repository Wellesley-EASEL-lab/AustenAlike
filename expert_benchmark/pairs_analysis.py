import csv
import sys
from scipy import stats
from sklearn.metrics import jaccard_score
"""
Script for comparing cosine similarity and expert pairings
"""

def convert_sims(line):
	for k,v in line.items():
		if k != 'character':
			line[k] = float(v)  # Convert similiarities to floats
	del line[line['character']]  #Remove self-similiarities
	del line['character']
	return line

def read_character_data(f):
	data = {}
	with open(f,'r') as of:
		reader = csv.DictReader(of)
		for line in reader:
			character = line['character']
			data[character] = convert_sims(line)
		return data

def read_benchmark_data(char_map,data): 
	benchmark = {}
	with open("expert-benchmark.csv",'r') as of:
		reader = csv.DictReader(of)
		for line in reader:
			char1 = char_map[line['Character']]
			char2 = char_map[line['Character2']]
			if char1 in data and char2 in data:
				n = int(line['Count'])
				if char1 not in benchmark:
					benchmark[char1] = {char2:n}
				else:
					benchmark[char1][char2] = n
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

def top_n_characters(benchmark,character,n,excludeMap=None):
	pairs = benchmark[character].items()
	if excludeMap:
		book = excludeMap[character]
		pairs = [p for p in pairs if excludeMap[p[0]] != book]
	return [i[0] for i in sorted(pairs,key=lambda x:-x[1])][:n]

def top_n_sims(data,character,n,excludeMap=None):
	pairs = data[character].items()
	if excludeMap:
		book = excludeMap[character]
		pairs = [p for p in pairs if excludeMap[p[0]] != book]
	return [i[0] for i in sorted(pairs,key=lambda x:x[1],reverse=True)][:n]

def top_in_topk(data,benchmark,n,novel_map):
	successes = []
	exSuccesses = []
	results = []
	for char in benchmark:
		topChar = top_n_characters(benchmark,char,1)[0]
		topN = top_n_sims(data,char,n)
		success = int(topChar in topN)
		successes.append(success)
		results.append([char,topChar,success,0,f"Top{n}success"])
		
		topExChars = top_n_characters(benchmark,char,1,excludeMap=novel_map)
		if len(topExChars):
			topExChar = topExChars[0]
			topExN = top_n_sims(data,char,n,excludeMap=novel_map)
			success = int(topExChar in topExN)
			exSuccesses.append(success)
			results.append([char,topExChar,success,1,f"Top{n}success"])
	print(f"Average top-{n}:",sum(successes)/len(successes))
	print(f"Average top-{n} excluding novel:",sum(exSuccesses)/len(exSuccesses))
	return successes,exSuccesses,results

def get_ranked_sims(data,lst,character):
	pairs = [(i,data[character][k]) for i,k in enumerate(lst)]
	return [i[0] for i in sorted(pairs,key=lambda x:x[1],reverse=True)]

def kendallT(data,benchmark,n,novel_map):
	taus = []
	exTaus = []
	results = []
	for char in benchmark:
		topChars = top_n_characters(benchmark,char,n)
		rankedSims = get_ranked_sims(data,topChars,char)
		res = stats.kendalltau(range(len(topChars)),rankedSims)
		taus.append(res.correlation)
		results.append([char,None,res.correlation,0,"KendallTau"])

		topExChars = top_n_characters(benchmark,char,n,excludeMap=novel_map)
		if len(topExChars):
			rankedExSims = get_ranked_sims(data,topExChars,char)
			res = stats.kendalltau(range(len(topExChars)),rankedExSims)
			exTaus.append(res.correlation)
			results.append([char,None,res.correlation,1,"KendallTau"])
	print(f"Average {n} Kendall T:",sum(taus)/len(taus))
	print(f"Average {n} Kendall T excluding novel:",sum(exTaus)/len(exTaus))
	return taus,exTaus,results

def getJaccard(data,benchmark,n,novel_map):
	taus = []
	exTaus = []
	results = []
	for char in benchmark:
		topChars = top_n_characters(benchmark,char,n)
		topSims = top_n_sims(data,char,len(topChars))
		res = jaccard_score(topChars,topSims,average='micro')
		taus.append(res)
		results.append([char,None,res,0,"Jaccard"])

		topExChars = top_n_characters(benchmark,char,n,excludeMap=novel_map)
		topExSims = top_n_sims(data,char,len(topExChars),excludeMap=novel_map)
		res = jaccard_score(topExChars,topExSims,average='micro')
		exTaus.append(res)
		results.append([char,None,res,1,"Jaccard"])
	print(f"Average {n} Jaccard:",sum(taus)/len(taus))
	print(f"Average {n} Jaccard excluding novel:",sum(exTaus)/len(exTaus))
	return taus,exTaus,results

def export(tag,data):
	header = ["dataset","character","topCharacter","result","excludeNovel","metric"]
	with open(f"{tag}_expert_results.csv",'w') as of:
		writer = csv.writer(of)
		writer.writerow(header)
		for r in data:
			writer.writerow([tag]+r)

def main():
	f = sys.argv[1]
	tag = sys.argv[2]
	novel_map = read_character_list()
	char_map = read_char_map()
	data = read_character_data(f)
	benchmark = read_benchmark_data(char_map,data)
	successes, exSuccesses, resT = top_in_topk(data,benchmark,10,novel_map)
	taus, exTaus, resK = kendallT(data,benchmark,10,novel_map)
	jaccard, exJaccard, resJ = getJaccard(data,benchmark,10,novel_map)
	lines = resT+resJ+resK
	export(tag,lines)

main()