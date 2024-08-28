import csv
import sys

"""
Script for analyzing similarity by narratological role
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
	with open("austen-social.tsv",'r') as of:
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

def most_similar_in_set(data,benchmark,novel_map,exclude_same_novel=False):
	all_comps = []
	for comparison in benchmark:
		top = []
		for category,charList in benchmark[comparison].items():
			top_cat = []
			for character in charList:
				if character not in data:
					print("Missing",character)
					continue
				characterDict = data[character]
				if exclude_same_novel:
					top_sim = max([(v,k) for k,v in characterDict.items() if novel_map[k]!=novel_map[character]])
					exclude = 1
				else:
					top_sim = max([(v,k) for k,v in characterDict.items()])
					exclude = 0
				topNovel = novel_map[top_sim[1]]
				top_cat.append([int(top_sim[1] in charList),comparison,category,exclude,novel_map[character],character,top_sim[1],topNovel])
			print(comparison.upper(),category)
			print(sum([i[0] for i in top_cat])/len(top_cat))
			top += top_cat
		print("OVERALL",comparison.upper())
		print(sum([i[0] for i in top])/len(top))
		all_comps += top
	return all_comps

def out_versus_in(data,benchmark,novel_map,exclude_same_novel=False):
	all_comps = []
	for comparison in benchmark:
		in_out_diffs = []
		for category,charList in benchmark[comparison].items():
			diffs_cat = []
			for character in charList:
				if character not in data:
					print("Missing",character)
					continue
				characterDict = data[character]
				if exclude_same_novel:
					in_sims = [v for k,v in characterDict.items() if k in charList and novel_map[k]!=novel_map[character]]
					out_sims = [v for k,v in characterDict.items() if k not in charList and novel_map[k]!=novel_map[character]]
					exclude = 1
				else:
					in_sims = [v for k,v in characterDict.items() if k in charList]
					out_sims = [v for k,v in characterDict.items() if k not in charList]
					exclude = 0
				if out_sims:
					outgroup_mean = sum(out_sims)/len(out_sims)
				if in_sims:
					ingroup_mean = sum(in_sims)/len(in_sims)
				diffs_cat.append([(1+ingroup_mean)-(1+outgroup_mean),comparison,category,exclude,novel_map[character],character,ingroup_mean,outgroup_mean])
			print(comparison.upper(),category)
			print(sum([i[0] for i in diffs_cat])/len(diffs_cat))
			in_out_diffs += diffs_cat
		print("OVERALL",comparison.upper())
		print(sum([i[0] for i in in_out_diffs])/len(in_out_diffs))
		all_comps += in_out_diffs
	return all_comps

def export_all(top_all,top_ex,diff_all,diff_ex,tag):
	export("social_topsim.csv",top_all+top_ex,["Top_in_group","comparison","category","exclude","novel","character","top","topNovel"],tag)
	export("social_simdiffs.csv",diff_all+diff_ex,["Sim_diffs","comparison","category","exclude","novel","character","simIn","simOut"],tag)

def export(outfix,data,header,tag):
	header = ["dataset"] + header
	with open(f"{tag}_{outfix}",'w') as of:
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

	most_all = most_similar_in_set(data,benchmark,novel_map)
	most_ex = most_similar_in_set(data,benchmark,novel_map,exclude_same_novel=True)
	diffs_all = out_versus_in(data,benchmark,novel_map)
	diffs_ex = out_versus_in(data,benchmark,novel_map,exclude_same_novel=True)
	export_all(most_all,most_ex,diffs_all,diffs_ex,tag)

main()