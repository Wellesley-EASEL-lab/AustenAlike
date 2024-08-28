import sys
import json
from collections import Counter

def clean_name(n):
	if "a " == n[:2].lower(): 
		n = n[2:]
	if "dear " == n[:5].lower() or "poor " == n[:5].lower():
		n = n[5:]
	return n

def get_name(name,cmap):
	stripped = clean_name(name).strip('-').strip(",").strip(".")
	if name in cmap:
		return cmap[name]
	elif stripped in cmap:
		return cmap[stripped]
	return name

def counts_and_max(d):
	total = {}
	for m in d['mentions']['proper']:
		total[m['n']] = m['c']
	if total != {}:
		most = sorted(total.items(),key=lambda x:-x[1])[0][0]
	else:
		most = None
	for m in d['mentions']['common']:
		total[m['n']] = m['c']
	if total != {} and most == None:
		most = sorted(total.items(),key=lambda x:-x[1])[0][0]
	for m in d['mentions']['pronoun']:
		total[m['n']] = m['c']
	if most == None:
		most = sorted(total.items(),key=lambda x:-x[1])[0][0]
	return most, sum([v for k,v in total.items()]), total


def read_data(book):
	ids = {}
	with open(f"../output_dir/{book}/{book}.book") as of:
		data = json.load(of)["characters"]
	for d in data:
		top, n, allMentions = counts_and_max(d)
		d['most'] = top
		d['total'] = n
		d['all'] = allMentions
		ids[d['id']] = d

	return ids

def merge_counts(d1,d2):
	new = {}
	for k in d1:
		if k in d2:
			v = d1[k] + d2[k]
			new[k] = v
		else:
			new[k] = d1[k]
	for k in d2:
		if k in d1:
			v = d1[k] + d2[k]
			new[k] = v
		else:
			new[k] = d2[k]
	return new

def combine(found):
	combined = {}
	for char in found:
		combined[char] = {}
		reps = found[char]
		combined[char]['agent'] = []
		combined[char]['patient'] = []
		combined[char]['mod'] = []
		combined[char]['poss'] = []
		combined[char]['id'] = []
		combined[char]['count'] = 0
		combined[char]['mentions'] = {'proper':[],'common':[],'pronoun':[]}
		for r in reps:
			combined[char]['agent'] += r['agent']
			combined[char]['patient'] += r['patient']
			combined[char]['mod'] += r['mod']
			combined[char]['poss'] += r['poss']
			combined[char]['id'] += [r['id']]
			combined[char]['count'] += r['count']
			combined[char]['mentions']['proper'] += r['mentions']['proper']
			combined[char]['mentions']['common'] += r['mentions']['common']
			combined[char]['mentions']['pronoun'] += r['mentions']['pronoun']
	return combined

def sort(ids,cmap):
	found = {}
	for i in ids:
		data = ids[i]
		if data['total'] > 5 and (data['mentions']['proper']!=[] or data['mentions']['common']!=[]):
			most = data['most']
			char = get_name(most,cmap)
			if char in cmap:
				if char in found:
					found[char] += [data]
				else:
					found[char] = [data]
			else:
				pass
				print(i)
				print(data['most'])
				print(data['total'])
				print(data['all'])
				print("--------------------------")
	return found

def export(data,book):
	with open(f"../booknlp-combined/{book}.json",'w') as of:
		for d in data:
			data[d]['character'] = d
		of.write(json.dumps([data[d] for d in data]))

def read_char_map(book):
	books = {"northanger":"NA","persuasion":"P","sense":"S&S","pride":"P&P","mansfield":"MP","emma":"E"}
	cmap = {}
	with open("../../character_map.tsv") as of:
		lines = [l.strip().split('\t') for l in of.readlines()]
	for l in lines:
		if l[0] == books[book]:
			cmap[l[1]] = l[2]
	return(cmap)


def main():
	book = sys.argv[1]
	ids = read_data(book)
	charMap = read_char_map(book)
	found = sort(ids,charMap)
	combo = combine(found)
	export(combo,book)


main()