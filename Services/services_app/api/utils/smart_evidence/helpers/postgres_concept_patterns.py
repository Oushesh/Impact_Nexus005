import os
from pathlib import Path

import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler
from tqdm import tqdm

from smart_evidence.helpers.concept_stores import (
    get_concepts,
)


def create_concept_patterns(
    nlp: Language,
    out_path: Path = Path("assets/keywords_clean/patterns_postgres.jsonl"),
):

    concepts = get_concepts()
    print(f"Number of company concepts to link with: {len(concepts)}")

    ruler = EntityRuler(nlp)
    ruler.add_patterns(concepts_to_patterns(nlp, concepts))
    out_path.parent.mkdir(exist_ok=True)
    ruler.to_disk(out_path)


def concepts_to_patterns(nlp, concepts, entity_label):
    def iterate_keywords(concepts):
        for concept in concepts:
            if "Keywords" in concept:
                yield from ((keyword, concept) for keyword in concept["Keywords"])
            yield ((concept["label"], concept))

    for doc, concept in tqdm(nlp.pipe(iterate_keywords(concepts), as_tuples=True)):
        yield {
            "pattern": [
                {
                    "LEMMA": tok.lemma_.lower(),
                    "TAG": {
                        "IN": [
                            "TO",
                            "DT",
                            "IN",
                            "CC",
                            "CD",
                            "HYPH",
                            "-LRB-",
                            "-RRB-",
                            "JJ",
                            "JJR",
                            "JJS",
                            "RB",
                            "RBR",
                            "RBS",
                            "RP",
                            "VBG",
                            "VBN",
                            "NN",
                            "NNP",
                            "NFP",
                            "NNPS",
                            "NNS",
                            "ADJ",
                            "ADP",
                        ]
                    },
                }
                for tok in doc
            ],
            "label": concept["kind"],
            "id": str(concept["id"]),
        }


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    create_concept_patterns(nlp)
