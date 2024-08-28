from booknlp.booknlp import BookNLP
import sys

which=sys.argv[1]

model_params={
		"pipeline":"entity,quote,supersense,event,coref", 
		"spacy_model": "en_core_web_trf",
                "model":"big"
	}
	
booknlp=BookNLP("en", model_params)

# Input file to process
input_file=f"{which}.txt"

# Output directory to store resulting files in
output_directory=f"output_dir/{which}/"

# File within this directory will be named ${book_id}.entities, ${book_id}.tokens, etc.
book_id=f"{which}"

booknlp.process(input_file, output_directory, book_id)
