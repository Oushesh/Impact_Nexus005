from typing import Any, List

import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from thefuzz import fuzz


class FuzzConceptExtractor:
    # A list of concepts should be given at the initialization.
    # An example of concepts_list is ['cement', 'greenhouse gas', 'limestone']
    def __init__(self, concepts_list: List[Any], **data: Any):
        self.method = data.get("method", "cosine")
        self.threshold = data.get("threshold", 0.65)
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.sw = stopwords.words("english")

        self.concepts = concepts_list

        # This is the list of lemmatized concepts
        self.concepts_lemmas = []
        for c in concepts_list:
            doc = self.nlp(c)
            self.concepts_lemmas.append(" ".join([token.lemma_ for token in doc]))

    # This is term frequency similarity. It is used for calculating similarity between
    # the concepts and the chunks of text.
    def tf_similarity(self, X, Y):

        X_list = word_tokenize(X)
        Y_list = word_tokenize(Y)

        for a in range(len(X_list)):
            for b in range(len(Y_list)):
                r = fuzz.ratio(X_list[a], Y_list[b])
                if (r > 75) and (r < 100):
                    X_list[a] = Y_list[b]

        sim = 0
        for i in X_list:
            if i in Y_list:
                sim += 1

        return sim / len(X_list)

    # This is cosine simliarity
    def cosine_similarity(self, X, Y):

        X_list = word_tokenize(X)
        Y_list = word_tokenize(Y)

        for a in range(len(X_list)):
            for b in range(len(Y_list)):
                r = fuzz.ratio(X_list[a], Y_list[b])
                if (r > 75) and (r < 100):
                    X_list[a] = Y_list[b]

        l1 = []
        l2 = []

        X_set = {w for w in X_list if not w in self.sw}
        Y_set = {w for w in Y_list if not w in self.sw}

        rvector = X_set.union(Y_set)
        for w in rvector:
            if w in X_set:
                l1.append(1)  # create a vector
            else:
                l1.append(0)
            if w in Y_set:
                l2.append(1)
            else:
                l2.append(0)
        c = 0

        for i in range(len(rvector)):
            c += l1[i] * l2[i]

        cosine = c / (float((sum(l1) * sum(l2)) ** 0.5) + 0.000001)
        return cosine

    # The text contains the text that concepts will be extracted from. Threshold is the
    # threshold of similarity for concept extraction. Higher threshold will result in
    # more false negatives, and lower threshold will result in more false positives.
    # The default method for similarity is cosine. But it can be changed to 'tf'.
    # An example of text is: 'We try to reduce emissiosn of greenhouse gas'.

    def __call__(self, text, **data: Any) -> List[str]:
        extracted_concepts = []
        doc = self.nlp(text)
        text_split = [token.lemma_.lower() for token in doc]

        if self.method == "cosine":
            similarity = self.cosine_similarity
        elif self.method == "tf":
            similarity = self.tf_similarity
        else:
            raise NotImplementedError

        for i, lemma in enumerate(self.concepts_lemmas):
            lemma = lemma.lower()

            flag = True
            for cw in lemma.split():
                if not cw in text_split:
                    flag = False
                    break
            if not flag:
                continue

            n = len(lemma.split()) + 2
            n = min(n, len(text_split))

            chunks = [
                " ".join(text_split[i : i + n])
                for i in range(0, len(text_split) - n + 1)
            ]
            for chunk in chunks:
                if similarity(lemma, chunk.lower()) > self.threshold:
                    extracted_concepts.append(self.concepts[i])

        return list(set(extracted_concepts))
