import nltk
import random

nltk.download('punkt') #No need of spacy for english punctuation

f = open("Services/DVC/perturbation_test/data/raw.txt")
corpus = f.read()


# Split into sentences
sent_list = nltk.tokenize.sent_tokenize(corpus)
# Remove any sentences that are suspiciously short - say <= 20 characters
clean_list = [s for s in sent_list if len(s) > 20]

# Randomly select 1000 for testing
random.seed(1)
keep = random.sample(clean_list, 500)

# Write this subset to file and test if the reports are properly written
with open('Services/DVC/perturbation_test/data/test_set.tsv', 'w') as f:
    for item in keep:
        # Remove any newlines in the body of the text to avoid confusion
        f.write("%s\t" % item.strip())


# CML and dvc does the check
