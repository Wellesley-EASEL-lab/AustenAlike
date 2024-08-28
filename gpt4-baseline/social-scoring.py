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
	with open("../social_benchmark/austen-social.tsv",'r') as of:
		reader = csv.DictReader(of,delimiter='\t')
		for line in reader:
			char = char_map[line['name']]
			if char not in data:
				print("Missing",char)
			else:
				for cat in ['startIncome','endIncome','gender','age','estAge','rank','maritalStatus']:
					val = line[cat]
					if cat not in benchmark:
						benchmark[cat] = {val:[char]}
					else:
						if val in benchmark[cat]:
							benchmark[cat][val].append(char)
						else:
							benchmark[cat][val] = [char]
		benchmark['age'] = bin_age(benchmark)
		del benchmark['estAge']
		benchmark['income'] = bin_income(benchmark)
		del benchmark['startIncome']
		del benchmark['endIncome']
	#for k in benchmark:
	#	print(k,benchmark[k].keys(),[len(benchmark[k][i]) for i in benchmark[k]])
	for k,v in benchmark['rank'].items():
		print(k,len(v))
	for k,v in benchmark['maritalStatus'].items():
		print(k,len(v))
	for k,v in benchmark['gender'].items():
		print(k,len(v))
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
	ages = data['age']
	estAges = data['estAge']
	for k,v in ages.items():
		all_ages += [(int(k),i) for i in v if k.strip()]
	for k,v in estAges.items():
		all_est_ages += [(int(k),i) for i in v]
	age_pairs = all_ages + [(k,v) for k,v in all_est_ages if v not in [z[1] for z in all_ages]]
	for age,char in age_pairs:
		ageDict[find_age_bin(age,bins)].append(char)
	for k,v in ageDict.items():
		print(k,len(v))
	return ageDict

def find_income_bin(income,bins):
	for i in bins:
		if i >= income:
			return i

def bin_income(data):
	startIncome = data['startIncome']
	endIncome = data['endIncome']
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
	for k,v in incomeDict.items():
		print(k,len(v))
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

def most_similar_in_set(data,benchmark,novel_map,exclude_same_novel=False):
	all_comps = []
	for comparison in benchmark:
		top = []
		for category,charList in benchmark[comparison].items():
			top_cat = []
			for character in charList:
				if character not in data or character not in novel_map:
					print("Missing",character)
					continue
				top_sim = data[character]
				novel = novel_map[character]
				exclude = 0
				topNovel = novel_map[top_sim]
				top_cat.append([int(top_sim in charList),comparison,category,exclude,novel_map[character],character,top_sim,topNovel])
			print(comparison.upper(),category)
			print(sum([i[0] for i in top_cat])/len(top_cat))
			top += top_cat
		print("OVERALL",comparison.upper())
		print(sum([i[0] for i in top])/len(top))
		all_comps += top
	return all_comps

def percent_in_group(data,benchmark,novel_map,exclude_same_novel=False):
	all_comps = []
	for comparison in benchmark:
		in_out_diffs = []
		for category,charList in benchmark[comparison].items():
			diffs_cat = []
			for character in charList:
				if character not in data or character not in novel_map:
					print("Missing",character)
					continue
				top_characters = [c for c in data[character] if c in novel_map]
				novel = novel_map[character]
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
			print(comparison.upper(),category)
			print(sum([i[0] for i in diffs_cat])/len(diffs_cat))
			in_out_diffs += diffs_cat
		print("OVERALL",comparison.upper())
		print(sum([i[0] for i in in_out_diffs])/len(in_out_diffs))
		all_comps += in_out_diffs
	return all_comps

def export_all(reason_top_all,plain_top_all,diff_all,diff_ex,tag):
	export("social_topsim.csv",reason_top_all,["Top_in_group","comparison","category","exclude","novel","character","top","topNovel"],tag+"-reasoning")
	export("social_topsim.csv",plain_top_all,["Top_in_group","comparison","category","exclude","novel","character","top","topNovel"],tag+"-plain")
	export("social_simdiffs.csv",diff_all+diff_ex,["Sim_diffs","comparison","category","exclude","novel","character","simIn","simOut"],tag)

def export(outfix,data,header,tag):
	header = ["dataset"] + header
	with open(f"results/{tag}_{outfix}",'w') as of:
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
	export_all(reason_most_all,plain_most_all,diffs_all,diffs_ex,tag)

main()