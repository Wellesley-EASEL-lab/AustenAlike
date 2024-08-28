import sys
import csv
from collections import Counter
from scipy import stats
from sklearn.metrics import jaccard_score

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

def make_top_dict(benchmark):
	closest = {}
	for c in benchmark:
		candidates = sorted(benchmark[c].items(),key=lambda x:x[1])
		closest[c] = candidates[-1][0]
	return closest

def get_top_n(benchmark,n=5):
	closest = {}
	for c in benchmark:
		candidates = sorted(benchmark[c].items(),key=lambda x:-x[1])
		closest[c] = [i[0] for i in candidates[:n]]
	return closest

def read_benchmark_data(char_map): 
	benchmark = {}
	with open("../expert_benchmark/expert-benchmark.csv",'r') as of:
		reader = csv.DictReader(of)
		for line in reader:
			char1 = char_map[line['Character']]
			char2 = char_map[line['Character2']]
			n = int(line['Count'])
			if char1 not in benchmark:
				benchmark[char1] = {char2:n}
			else:
				benchmark[char1][char2] = n
	return benchmark

def read_top1_results(f,char_map):
	results = {}
	with open(f,'r') as of:
		reader = csv.DictReader(of,delimiter="\t")
		for line in reader:
			char1 = char_map[line['Character']]
			char2 = char_map[line['MostCommon']]
			if char2 == char1:
				chars = Counter([line[k] for k in line if k!="Character" and k!="MostCommon" and line[k]!=char1])
				if len(chars):
					char2 = chars.most_common(1)
				else:
					print("SAME:",char1,f)
			results[char1] = char2
	return results

def score_top1_accuracy(benchmark,results):
	scores = []
	for c in benchmark:
		if c in results:
			scores.append(1 if benchmark[c] == results[c] else 0)
	print(sum(scores)/len(scores))
	return scores

def top1_in_topn_accuracy(benchmark,results):
	scores = []
	for c in results:
		if c in benchmark:
			scores.append(1 if results[c] in benchmark[c] else 0)
	print(sum(scores)/len(scores))
	return scores

def read_top_ranking(f,char_map,n=10):
	results = {}
	with open(f,'r') as of:
		of.readline()
		for line in of.readlines():
			bits = line.strip().split('\t')
			char1 = char_map[bits[0]]
			chars = [char_map[c] for c in bits[2:] if char_map[c]!=char1]
			if char1 in results:
				results[char1] += chars
			else:
				results[char1] = chars
			results[char1] = [c[0] for c in Counter(results[char1]).most_common(n)]
	return results

def kendallT(data,benchmark,n=10):
	taus = []
	exTaus = []
	results = []
	for char in benchmark:
		if char in data:
			gold = benchmark[char]
			guesses = data[char]
			res = stats.kendalltau(range(len(gold)),guesses)
			taus.append(res.correlation)

	print(f"Average {n} Kendall T:",sum(taus)/len(taus))
	return taus

def getJaccard(data,benchmark,n=10):
	taus = []
	exTaus = []
	results = []
	for char in benchmark:
		if char in data:
			gold = benchmark[char]
			guesses = data[char]
		res = jaccard_score(gold,guesses,average='micro')
		taus.append(res)

	print(f"Average {n} Jaccard:",sum(taus)/len(taus))
	return taus

def main():
	char_map = read_char_map()
	benchmark = read_benchmark_data(char_map)
	closest = make_top_dict(benchmark)
	top5 = get_top_n(benchmark,5)
	top10 = get_top_n(benchmark,10)
	plain_res = read_top1_results("plain_results_t02.tsv",char_map)
	print("Plain results:")
	score_top1_accuracy(closest,plain_res)
	top1_in_topn_accuracy(top5,plain_res)
	top1_in_topn_accuracy(top10,plain_res)
	reason_res = read_top1_results("reasoning_results_t02.tsv",char_map)
	print("Reasoning results:")
	score_top1_accuracy(closest,reason_res)
	top1_in_topn_accuracy(top5,reason_res)
	top1_in_topn_accuracy(top10,reason_res)

	for k in [10,5,3,2]:
		print(f"Ranking results for n={k}:")
		top = get_top_n(benchmark,k)
		topranking = read_top_ranking("top10_results_t02.tsv",char_map,k)
		#for k,v in topranking.items():
		#	if len(v) != 10:
		#		print(k,v)
		taus = kendallT(topranking,top,k)
		jaccard = getJaccard(topranking,top,k)

main()