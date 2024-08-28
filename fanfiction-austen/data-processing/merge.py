import sys
import os
import json
import csv
from collections import Counter

def clean_name(n):
	if "a " == n[:2].lower(): 
		n = n[2:]
	if "dear " == n[:5].lower() or "poor " == n[:5].lower():
		n = n[5:]
	return n

def read_char_map(book):
	books = {"northanger":"NA","persuasion":"P","sense":"S&S","pride":"P&P","mansfield":"MP","emma":"E"}
	cmap = {}
	with open("../../character_map.tsv") as of:
		lines = [l.strip().split('\t') for l in of.readlines()]
	for l in lines:
		if l[0] == books[book]:
			cmap[l[1]] = l[2]
	return(cmap)

def get_name(name,cmap):
	stripped = clean_name(name).strip('-').strip(",").strip(".")
	if name in cmap:
		return cmap[name]
	elif stripped in cmap:
		return cmap[stripped]
	return name

def get_clusters(book):
	path = f"../output/{book}/char_coref"
	all_clusters = []
	for f in os.listdir(path):
		with open(path+"/"+f,'r') as of:
			data = json.load(of)['clusters']
		for d in data:
			all_clusters.append(d)
	return all_clusters

def get_assertions(book):
	path = f"../output/{book}/assertion_extraction"
	all_clusters = []
	for f in os.listdir(path):
		with open(path+"/"+f,'r') as of:
			data = json.load(of)
		all_clusters.append(data)
	return all_clusters

def get_quotes(book):
	path = f"../output/{book}/quote_attribution"
	all_clusters = []
	for f in os.listdir(path):
		with open(path+"/"+f,'r') as of:
			data = json.load(of)
		all_clusters.append(data)
	return all_clusters

def merge_clusters(clusters,cmap):
	characters = {}
	missing = []
	for c in clusters:
		name = get_name(c['name'],cmap)		
		if name in cmap:
			if name in characters:
				characters[name]['mentions'] += c['mentions']
			else:
				characters[name] = {"mentions": c['mentions']}
		else:
			if name not in missing:
				missing.append(name)
	#for m in sorted(missing):
	#	print(m)
	return characters

def merge_assertions(assertions,characters,cmap):
	for a in assertions:
		for char in a:
			name = get_name(char,cmap)
			data = a[char]
			if name in cmap:
				assert name in characters
				if "assertions" in characters[name]:
					characters[name]["assertions"] += data
				else:
					characters[name]["assertions"] = data
			else:
				pass
	return characters

def merge_quotes(quotes,characters,cmap):
	for q in quotes:
		for char in q:
			name = get_name(char,cmap)
			data = q[char]
			if name in cmap:
				assert name in characters
				if "quotes" in characters[name]:
					characters[name]["quotes"] += data
				else:
					characters[name]["quotes"] = data
			else:
				pass
	return characters

def export(book,data):
	with open(f"../fanfic-combined/{book}.json",'w') as of:
		for d in data:
			data[d]['character'] = d
		of.write(json.dumps([data[d] for d in data]))

	with open(f"../fanfic-assertions/{book}_assertions.tsv",'w') as of:
		writer = csv.writer(of,delimiter='\t')
		writer.writerow(["Character","Assertion"])
		for char in data:
			if "assertions" in data[char]:
				for e in data[char]["assertions"]:
					row = [char,e["text"]]
					writer.writerow(row)

	with open(f"../fanfic-quotes/{book}_quotes.tsv",'w') as of:
		writer = csv.writer(of,delimiter='\t')
		writer.writerow(["Character","Quote"])
		for char in data:
			if "quotes" in data[char]:
				for e in data[char]["quotes"]:
					row = [char,e["text"]]
					writer.writerow(row)

def main():
	book = sys.argv[1]
	charMap = read_char_map(book)
	all_clusters = get_clusters(book)
	all_quotes = get_quotes(book)
	all_assertions = get_assertions(book)
	characters = merge_clusters(all_clusters,charMap)
	characters = merge_assertions(all_assertions,characters,charMap)
	characters = merge_quotes(all_quotes,characters,charMap)
	export(book,characters)

main()