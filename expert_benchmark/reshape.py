import csv

def read_char_map():
	m = {}
	with open("../character_map.tsv",'r') as of:
		reader = csv.reader(of,delimiter="\t")
		for line in reader:
			book = line[0]
			alias = line[1]
			name = line[2]
			m[alias] = book
	return m

novel_map = read_char_map()

with open("character_pair_counts.tsv",'r') as of:
	reader = csv.DictReader(of,delimiter='\t')
	lines = [d for d in reader]

charDict = {}
for l in lines:
	char = l['Character']
	char2 = l['Character2']
	count = l['Count']
	if char not in charDict:
		charDict[char] = {char2:count}
	else:
		charDict[char][char2] = count


with open("expert-benchmark.csv",'w') as of:
	writer = csv.writer(of)
	writer.writerow(['Character',"Novel","Character2","Novel1","Count"])
	for character in charDict:
		for char2 in charDict:
			count = charDict[character][char2] if char2 in charDict[character] else 0
			line = [character,novel_map[character],char2,novel_map[char2],count]
			writer.writerow(line)


