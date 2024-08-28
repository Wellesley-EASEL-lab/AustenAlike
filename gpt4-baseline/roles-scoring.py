import csv
import sys
from collections import Counter
"""
Script for analyzing similarity by narratological role
"""

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

def read_top_ranking(f,char_map):
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
			results[char1] = [c[0] for c in Counter(results[char1]).most_common()]
	return results

def read_benchmark_data(char_map,data): 
	benchmark = {}
	with open("../role_benchmark/austen-roles.tsv",'r') as of:
		reader = csv.reader(of,delimiter='\t')
		for char,novel,role in reader:
			char = char_map[char]
			if role not in benchmark:
				benchmark[role] = [char]
			else:
				benchmark[role].append(char)
			if char not in data:
				print("Missing",char)
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
					char2 = chars.most_common(1)[0][0]
				else:
					print("SAME:",char1,f)
			results[char1] = char2
	return results

def most_similar_in_set(data,benchmark,novel_map):
	"""How often is the top character in the same role set?"""
	top = []
	for category,charList in benchmark.items():
		top_cat = []
		for character in charList:
			novel = novel_map[character]
			if character not in data:
				print("Missing",character)
				continue
			top_sim = data[character]
			exclude = 'All'
			top_novel = novel_map[top_sim]
			top_cat.append([int(top_sim in charList),category,int(exclude=="ExcludeSameNovel"),novel,character,top_sim,top_novel])
		top += top_cat
	return top

def percent_in_group(data,benchmark,novel_map,exclude_same_novel=False):
	in_out_diffs = []
	for category,charList in benchmark.items():
		diffs_cat = []
		for character in charList:
			novel = novel_map[character]
			if character not in data:
				print("Missing",character)
				continue
			top_characters = [c for c in data[character] if c in novel_map] 
			if exclude_same_novel:
				in_sims = [v for v in top_characters if v in charList and novel_map[v]!=novel_map[character]]
				out_sims = [v for v in top_characters if v not in charList and novel_map[v]!=novel_map[character]]
				exclude = "ExcludeSameNovel"
			else:
				in_sims = [v for v in top_characters if v in charList]
				out_sims = [v for v in top_characters if v not in charList]
				exclude = 'All'
			in_ratio = len(in_sims)/len(in_sims+out_sims) if len(in_sims+out_sims) else -1
			diffs_cat.append([in_ratio,category,int(exclude=="ExcludeSameNovel"),novel,character,len(in_sims),len(out_sims)])
		in_out_diffs += diffs_cat
	return in_out_diffs

def export_all(plain_most_all,reason_most_all,diff_all,diff_ex,tag):
	export("group_topsim.csv",reason_most_all,["Top_in_group","category","exclude","novel","character","top","topNovel"],tag+"-reasoning")
	export("group_topsim.csv",plain_most_all,["Top_in_group","category","exclude","novel","character","top","topNovel"],tag+"-plain")
	export("group_inpercent.csv",diff_all+diff_ex,["In_Percent","category","exclude","novel","character","simIn","simOut"],tag)

def export(outfix,data,header,tag):
	header = ["dataset"] + header
	with open(f"role-results/{tag}_{outfix}",'w') as of:
		writer = csv.writer(of)
		writer.writerow(header)
		for r in data:
			writer.writerow([tag]+r)

def main():
	tag = "gpt4"
	novel_map = read_character_list()
	char_map = read_char_map()
	topranking = read_top_ranking("top10_results_t02.tsv",char_map)
	benchmark = read_benchmark_data(char_map,topranking)
	plain_tops = read_top1_results("plain_results_t02.tsv",char_map)
	reason_tops = read_top1_results("reasoning_results_t02.tsv",char_map)

	plain_most_all = most_similar_in_set(plain_tops,benchmark,novel_map)
	reason_most_all = most_similar_in_set(reason_tops,benchmark,novel_map)
	
	diffs_all = percent_in_group(topranking,benchmark,novel_map)
	diffs_ex = percent_in_group(topranking,benchmark,novel_map,exclude_same_novel=True)
	export_all(plain_most_all,reason_most_all,diffs_all,diffs_ex,tag)
	
main()