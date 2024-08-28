"""
Script for processing character similarity pairs
"""

def main():
	with open("austen-pairs.tsv",'r') as of:
		lines = [l.strip().split('\t') for l in of.readlines()]
	char_dict = {}
	for l in lines:
		char1 = l[0]
		char2 = l[1]
		if (char1,char2) in char_dict:
			char_dict[(char1,char2)] +=1
		else:
			char_dict[(char1,char2)] = 1
		if (char2, char1) in char_dict:
			char_dict[(char2,char1)] +=1
		else:
			char_dict[(char2,char1)] = 1


	for k,v in sorted(char_dict,key=lambda x:(x[0],-char_dict[x],x[1])):
		print(k+'\t'+v+'\t'+str(char_dict[(k,v)]))


main()

