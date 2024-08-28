import sys
import csv
import torch
import numpy as np
from transformers import AutoTokenizer, T5EncoderModel


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-11b")
model = T5EncoderModel.from_pretrained("google-t5/t5-11b",torch_dtype=torch.float16,device_map="auto")
SIZE = 1024

def get_path(book,kind,system):
	if system == "booknlp":
		return f"../booknlp-austen/booknlp-{kind}/{book}_{kind}.tsv"
	elif system == "fanfic":
		return f"../fanfiction-austen/fanfic-{kind}/{book}_{kind}.tsv"
	else:
		print("System not recognized")

def get_passages(book,kind,system):
	characters = {}
	loc = get_path(book,kind,system)
	with open(loc, 'r') as of:
		reader = csv.DictReader(of,delimiter="\t")
		lines = [r for r in reader]
	for l in lines:
		char = l["Character"]
		if char in characters:
			characters[char].append(l)
		else:
			characters[char] = [l]
	return characters

def find_index(w,c,input_ids):
	toks = input_ids.tolist()[0]
	w_toks = tokenizer(w).input_ids[:-1]
	assert tokenizer.decode(w_toks) == w
	idxs = [toks.index(w) for w in w_toks]
	if len(c.split(w)) == 2:
		idxs += [toks.index(w) for w in w_toks[idxs[-1]:]]
	return idxs

def index_embeds(idxs,hidden_states):
	embeds = []
	for i in idxs:
		embed = hidden_states[0][i]
		embeds.append(embed)
	return embeds

def get_embeddings(passages,kind):
	embeds = []
	for p in passages:
		w = p["Event"] if kind == "events" else p["Modifier"]
		c = p['Context']
		input_ids = tokenizer(c,return_tensors="pt").input_ids.to(1)
		i = find_index(w,c,input_ids)
		with torch.no_grad():
			outputs = model(input_ids=input_ids)
		last_hidden_states = outputs.last_hidden_state
		embed = index_embeds(i,last_hidden_states)
		embeds += embed
	return embeds

def average_embeds(embeds):
	print(embeds[0].shape)
	all_embeds = torch.stack(embeds)
	print(all_embeds.shape)
	avg = torch.mean(all_embeds,dim=0)
	print(avg.shape)
	return avg.tolist()
	
def by_character_events(characters):
	embedDict = {}
	for c in characters:
		agent = [e for e in characters[c] if e['Role']=="agent"]
		patient = [e for e in characters[c] if e['Role']=="patient"]
		if agent:
			ag_embeds = get_embeddings(agent,"events")
			ag_avg = average_embeds(ag_embeds)
		else:
			ag_avg = [0]*SIZE
		if patient:
			pat_embeds = get_embeddings(patient,"events")
			pat_avg = average_embeds(pat_embeds)
		else:
			pat_avg = [0]*SIZE
		embedDict[c] = ag_avg+pat_avg

	return embedDict

def by_character_modifiers(characters):
	embedDict = {}
	for c in characters:
		data = characters[c]
		embeds = get_embeddings(data,"modifiers")
		embedDict[c] = average_embeds(embeds)
	return embedDict

def export(book,kind,system,embeds):
	with open(f"computed_embeddings/{system}/{book}_{kind}.tsv",'w') as of:
		for char in embeds:
			line = [book,char]+embeds[char]
			of.write("\t".join([str(s) for s in line])+'\n')

def main():
	book = sys.argv[1]
	kind = sys.argv[2]
	system = sys.argv[3]
	passages = get_passages(book,kind,system)
	if kind == "events":
		embeds = by_character_events(passages)
	elif kind == "modifiers":
		embeds = by_character_modifiers(passages)
	else:
		print("Kind not recognized!")
	export(book,kind,system,embeds)

main()