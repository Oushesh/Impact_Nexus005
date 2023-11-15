from spacy.language import Language


@Language.component("lower_case_lemmas")
def lower_case_lemmas(doc):
    for token in doc:
        token.lemma_ = token.lemma_.lower()
    return doc
