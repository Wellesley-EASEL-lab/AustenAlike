import sys
import json
import csv
from collections import Counter

def read_data(book):
	ids = {}
	with open(f"../booknlp-combined/{book}.json",'r') as of:
		data = json.load(of)
	return data

def organize_quotes(lines):
	quotes = {}
	for line in lines:
		char = int(line[5])
		quote = line[6]
		if char not in quotes:
			quotes[char] = [quote]
		else:
			quotes[char] += [quote]
	return quotes

def read_quotes(book):
	with open(f"../output_dir/{book}/{book}.quotes",'r') as of:
		lines = [d.strip().split('\t') for d in of.readlines()]
	head = lines[0]
	lines = lines[1:]
	quotes = organize_quotes(lines)
	return quotes

def process_character(c,quotes):
	all_quotes = []
	ids = c['id']
	for i in ids:
		if i in quotes:
			all_quotes += quotes[i]
	return [[c['character'],q] for q in all_quotes]

def export(events,book):
	with open(f"../booknlp-quotes/{book}_quotes.tsv",'w') as of:
		writer = csv.writer(of,delimiter='\t')
		writer.writerow(["Character","Quote"])
		for e in events:
			writer.writerow(e)

def main():
	book = sys.argv[1]
	all_q = []
	data = read_data(book)
	quotes = read_quotes(book)
	for c in data:
		q = process_character(c,quotes)
		all_q += q
	export(all_q,book)

main()