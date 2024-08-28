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
	with open("austen-roles.tsv",'r') as of:
		reader = csv.reader(of,delimiter='\t')
		for char,novel,role in reader:
			char = char_map[char]
			if char not in data:
				print("Missing",char)
			else:
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

def most_similar_in_set(data,benchmark,novel_map,exclude_same_novel=False):
	top = []
	for category,charList in benchmark.items():
		top_cat = []
		for character in charList:
			novel = novel_map[character]
			if character not in data:
				print("Missing",character)
				continue
			characterDict = data[character]
			if exclude_same_novel:
				top_sim = max([(v,k) for k,v in characterDict.items() if novel_map[k]!=novel_map[character]])
				exclude = "ExcludeSameNovel"
			else:
				top_sim = max([(v,k) for k,v in characterDict.items()])
				exclude = 'All'
			top_novel = novel_map[top_sim[1]]
			top_cat.append([int(top_sim[1] in charList),category,int(exclude=="ExcludeSameNovel"),novel,character,top_sim[1],top_novel])
		#print(category.upper())
		#print(sum([i[0] for i in top_cat])/len(top_cat))
		top += top_cat
	#print("OVERALL")
	#print(sum([i[0] for i in top])/len(top))
	return top

def out_versus_in(data,benchmark,novel_map,exclude_same_novel=False):
	in_out_diffs = []
	for category,charList in benchmark.items():
		diffs_cat = []
		for character in charList:
			novel = novel_map[character]
			if character not in data:
				print("Missing",character)
				continue
			characterDict = data[character]
			if exclude_same_novel:
				in_sims = [v for k,v in characterDict.items() if k in charList and novel_map[k]!=novel_map[character]]
				out_sims = [v for k,v in characterDict.items() if k not in charList and novel_map[k]!=novel_map[character]]
				exclude = "ExcludeSameNovel"
			else:
				in_sims = [v for k,v in characterDict.items() if k in charList]
				out_sims = [v for k,v in characterDict.items() if k not in charList]
				exclude = 'All'
			outgroup_mean = sum(out_sims)/len(out_sims)
			ingroup_mean = sum(in_sims)/len(in_sims)
			diffs_cat.append([(1+ingroup_mean)-(1+outgroup_mean),category,int(exclude=="ExcludeSameNovel"),novel,character,ingroup_mean,outgroup_mean])
		#print(category.upper())
		#print(sum([i[0] for i in diffs_cat])/len(diffs_cat))
		in_out_diffs += diffs_cat
	#print("OVERALL")
	#print(sum([i[0] for i in in_out_diffs])/len(in_out_diffs))
	return in_out_diffs

def export_all(top_all,top_ex,diff_all,diff_ex,tag):
	export("group_topsim.csv",top_all+top_ex,["Top_in_group","category","exclude","novel","character","top","topNovel"],tag)
	export("group_simdiffs.csv",diff_all+diff_ex,["Sim_diffs","category","exclude","novel","character","simIn","simOut"],tag)

def export(outfix,data,header,tag):
	header = ["dataset"] + header
	with open(f"results/{tag}_{outfix}",'w') as of:
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