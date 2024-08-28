for book in pride sense mansfield persuasion emma; do
	echo python nv-embeddings.py $book assertions fanfic
	python nv-embeddings.py $book assertions fanfic
	echo python nv-embeddings.py $book quotes fanfic
	python nv-embeddings.py $book quotes fanfic
	echo python nv-embeddings.py $book quotes booknlp
	python nv-embeddings.py $book quotes booknlp
	echo python t5-embeddings.py $book modifiers booknlp
	python t5-embeddings.py $book modifiers booknlp
	echo python t5-embeddings.py $book events booknlp
	python t5-embeddings.py $book events booknlp
done
