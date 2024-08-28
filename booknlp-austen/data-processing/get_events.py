import sys
import json
import csv
from collections import Counter

def read_data(book):
	ids = {}
	with open(f"../booknlp-combined/{book}.json",'r') as of:
		data = json.load(of)
	print(len(data))
	return data

def get_sents(lines):
	sentences = []
	curr = 0
	sent = ""
	for line in lines:
		if int(line[1]) != curr:
			sentences.append(sent)
			sent = line[4]+" "
			curr += 1
		else:
			sent += line[4]+" "
	sentences.append(sent)
	return sentences

def make_token_map(lines):
	tokens = {}
	for line in lines:
		tokens[int(line[3])] = int(line[1])
	print(len(tokens))
	return tokens

def read_tokens(book):
	with open(f"../output_dir/{book}/{book}.tokens",'r') as of:
		lines = [d.strip().split('\t') for d in of.readlines()]
	head = lines[0]
	lines = lines[1:]
	print(head)
	sentences = get_sents(lines)
	tokenMap = make_token_map(lines)
	return tokenMap, sentences

def process_character(c,tokens,sentences):
	agent = [retrieve_context(e,"agent",tokens,sentences) for e in c['agent']]
	patient = [retrieve_context(e,"patient",tokens,sentences) for e in c['patient']]
	events = [[c['character']]+e for e in agent+patient]
	return events

def retrieve_context(e,kind,tokens,sentences):
	tok_id = e['i']
	sent_id = tokens[tok_id]
	sentence = sentences[sent_id]
	assert e['w'] in sentence
	return [kind,e['w'],sentence]

def export(events,book):
	with open(f"../booknlp-events/{book}_events.tsv",'w') as of:
		writer = csv.writer(of,delimiter='\t')
		writer.writerow(["Character","Role","Event","Context"])
		for e in events:
			writer.writerow(e)

def main():
	book = sys.argv[1]
	all_events = []
	data = read_data(book)
	tokens,sentences = read_tokens(book)
	for c in data:
		events = process_character(c,tokens,sentences)
		all_events += events
	export(all_events,book)

main()