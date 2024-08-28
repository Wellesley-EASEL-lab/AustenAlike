import sys
import csv
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from torch.nn import DataParallel

"""
Only for embedding quotes and assertions. 
Events and modifiers need to be extracted from their contexts.
"""

# load model with tokenizer
model = AutoModel.from_pretrained('nvidia/NV-Embed-v1', trust_remote_code=True,use_auth_token="INSERT AUTH TOKEN",
    torch_dtype=torch.float16)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = model.to(device)
batchsize = 15

def get_path(book,kind,system):
	if system == "booknlp":
		return f"../booknlp-austen/booknlp-{kind}/{book}_{kind}.tsv"
	elif system == "fanfic":
		return f"../fanfiction-austen/fanfic-{kind}/{book}_{kind}.tsv"
	else:
		print("System not recognized")

def get_embeddings(passages):
	max_length = max([len(s) for s in passages]) #4096
	#print("Max length",max_length)
	embeddings = model.encode(passages, instruction="", max_length=max_length)

	# normalize embeddings
	#embeddings = F.normalize(embeddings, p=2, dim=1)
	return embeddings

def average_embeds(embeds):
	print(embeds.shape)
	avg = torch.mean(embeds,dim=0)
	print(avg.shape)
	return avg.tolist()

def merge_batches(batches):
	return torch.cat(batches)

def by_character(characters):
	embedDict = {}
	for c in characters:
		data = characters[c]
		print(len(data))
		if len(data) > batchsize:
			batches = []
			start = 0
			for i in range(len(data)//batchsize):
				embeds = get_embeddings(data[start:start+batchsize])
				batches.append(embeds)
				start += batchsize
			if data[start:]:
				embeds = get_embeddings(data[start:])
				batches.append(embeds)
			embeds = merge_batches(batches)
		else:
			embeds = get_embeddings(data)
		embedDict[c] = average_embeds(embeds)
	return embedDict	

def get_passages(book,kind,system):
	characters = {}
	loc = get_path(book,kind,system)
	with open(loc, 'r') as of:
		reader = csv.DictReader(of,delimiter="\t")
		lines = [r for r in reader]
	for l in lines:
		char = l["Character"]
		rest = l[kind[:-1].title()]
		if char in characters:
			characters[char].append(rest)
		else:
			characters[char] = [rest]
	return characters

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
	embeds = by_character(passages)
	export(book,kind,system,embeds)

main()

