from spacy.pipeline import EntityRuler
from spacy.language import Language
from pyairtable import Table
from tqdm import tqdm
from pathlib import Path
import spacy
import os


AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]


def create_concept_patterns(
    nlp: Language,
    out_path: Path = Path("assets/keywords_clean/patterns_airtable.jsonl"),
):
    company_concept_table = Table(
        AIRTABLE_API_KEY, "appGhfa7A73wMqhRB", "CompanyConcept"
    )
    formula = (
        f"NOT(OR({{State}}='DISCARDED', {{State}}='DISABLED', {{State}}='GENERATED'))"
    )
    rows = company_concept_table.all(view="Grid view", formula=formula)
    company_concepts = [
        {
            **CompanyConcept.from_airtable(**row).dict(),
            "type": "COMPANY",
        }
        for row in rows
    ]
    print(f"Gathered {len(company_concepts)} company concepts from Airtable.")

    impact_concept_table = Table(
        AIRTABLE_API_KEY, "appGhfa7A73wMqhRB", "ImpactConcept NEW"
    )
    formula = (
        f"NOT(OR({{State}}='DISCARDED', {{State}}='DISABLED', {{State}}='GENERATED'))"
    )
    rows = impact_concept_table.all(view="Grid view", formula=formula)
    impact_concepts = [
        {
            **ImpactConcept.from_airtable(**row).dict(),
            "type": "IMPACT",
        }
        for row in rows
    ]
    print(f"Gathered {len(impact_concepts)} impact concepts from Airtable.")

    ruler = EntityRuler(nlp)
    ruler.add_patterns(concepts_to_patterns(nlp, company_concepts + impact_concepts))
    # out_path.mkdir(exist_ok=True)
    ruler.to_disk(out_path)


def concepts_to_patterns(nlp, concepts):
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
            "label": concept["type"],
            "id": concept.get("id"),
        }


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_trf")
    create_concept_patterns(nlp)
