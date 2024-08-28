import sys
import json
import csv
from collections import Counter

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

def read_sentences(book):
	with open(f"../../booknlp-austen/output_dir/{book}/{book}.tokens",'r') as of:
		lines = [d.strip().split('\t') for d in of.readlines()]
	head = lines[0]
	lines = lines[1:]
	sentences = get_sents(lines)
	return sentences

def make_chapters(sentences):
	chapters = []
	chapter = []
	for s in sentences:
		if "CHAPTER" in s or "Chapter" in s:
			if "CHAPTER" in s:
				before,after = s.split("CHAPTER")
			else:
				before,after = s.split("Chapter")
			if before:
				chapter.append(before)
			chapters.append(chapter)
			if after:
				chapter = [after]
			else:
				chapter = []
		elif len(s.split(" ")) > 10000:
			splits = s.split(" ")
			first = " ".join(splits[:len(splits)//2])
			second = " ".join(splits[len(splits)//2:])
			chapter.append(first)
			chapter.append(second)
		elif s:
			chapter.append(s)
		else:
			pass
	chapters.append(chapter)
	return chapters

def mega_export(book, chapters,split):
	files = []
	chapterset = []
	for c in chapters:
		if len(chapterset) == split:
			files.append(chapterset)
			chapterset = [c]
		else:
			chapterset.append(c)
	files.append(chapterset)
	for i,f in enumerate(files):
		export(book+f"_{i}",book,f)


def export(book,d,chapters):
	with open(f"../preprocessed/{d}/{book}.csv",'w') as of:
		writer = csv.writer(of)
		writer.writerow(["fic_id","chapter_id","para_id","text","text_tokenized"])
		for i,c in enumerate(chapters):
			for j,s in enumerate(c):
				line = [book,i+1,j+1,s,s]
				writer.writerow(line)

def main():
	book = sys.argv[1]
	split = int(sys.argv[2])
	sentences = read_sentences(book)
	chapters = make_chapters(sentences)
	mega_export(book,chapters,split)

main()