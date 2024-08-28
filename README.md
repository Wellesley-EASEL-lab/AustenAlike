# AustenAlike
AustenAlike character similarity benchmark

# Austen data

For convenience, the repository contains the following files for character mapping:

+ austen-novels.tsv: maps characters to novels
+ character_map.tsv: alias list for all characters
+ characters.tsv: list of all included characters

# Constructing representations

## Pipeline data

The BookNLP and FanfictionNLP pipeline output can be found in the booknlp-austen and fanfiction-austen folders.

## Feature embeddings

Scripts for extracting contextualized embeddings for each kind of feature can be found in the embeddings folder. 

t5-embeddings.py is used to retrieve embeddings of single-word features (events and modifiers) using the 11B parameter version of T5. This will require a GPU with at least 48 GB of memory. 

nv-embeddings.py is used to retrieve embeddings of multi-sentence features (assertions and quotes) using the 7B version of NV-Embed.

The embeddings/run_all.sh script extracts all features for all books. 

The extracted embeddings are in embeddings/computed_embeddings

# Running the benchmark

## Computing similarity

The scripts folder contains scripts for computing cosine similarity between all pairs of characters. 

cosine_sim.py computes cosine similarity without centering embeddings; scaled_cosine_sim.py centers the embeddings first by subtracting the mean of all vectors from each vector.

## Benchmark Subsets

The scripts for running each of the three benchmarks are found in their respective folders: expert_benchmark, role_benchmark, and social_benchmark.

Each of these folders contains the scaled and unscaled cosine similarities relevant for the benchmark in the results and unscaled-results folders.

Each benchmark folder also contains:
+ an analysis script: pairs_analysis.py, social_roles_analysis.py, narratological_roles_analysis.py
+ a file containing the benchmark data: expert-benchmark.csv, austen-social.csv, austen-roles.tsv
+ an R script for statistical analysis: expert.Rmd, social.Rmd, roles.Rmd

## Clustering

We also performed clustering experiments for the Social and Narrative Role benchmarks, which were not included in the paper. You can find results for these experiments and the scripts that run them (social-clustering.py, role-clustering.py) in the benchmark folders.

## GPT-4 experiments

All scripts for the GPT-4 experiments and results can be found in the gpt4-baseline folder. reasoning.py runs the experiments, taking the experiment type as a flag:

python gpt4-baseline/reasoning.py plain

Scoring scripts are included for each benchmark.

# Attribution

Please cite our ArviX preprint:

