from typing import List
from spacy.language import Language
from pathlib import Path
from spacy.pipeline import EntityRuler
import yaml
from tqdm import tqdm

KEYWORD_FILE_PATHS = [
    "assets/keywords_clean/COMPANY.yaml",
    "assets/keywords_clean/IMPACT.yaml",
    "assets/keywords_clean/BANLIST.yaml",
]


def get_keywords_from_yamls(keyword_file_paths: List[str]):
    for keyword_path in keyword_file_paths:
        keyword_path = Path(keyword_path)

        with open(keyword_path) as f:
            keywords = yaml.load(f, Loader=yaml.FullLoader)
        ent_label = keyword_path.stem
        for concept_label, concept in keywords.items():
            concept_id = ";".join(concept["taxonomy_paths"]) + ";" + concept_label
            for synonym in concept["keywords"]["en"]:
                yield {
                    "keyword": synonym,
                    "label": ent_label,
                    "id": concept_id,
                    "concept_label": concept_label,
                }

def get_concepts_from_yamls(keyword_file_paths: List[str]):
    for keyword_path in keyword_file_paths:
        keyword_path = Path(keyword_path)

        with open(keyword_path) as f:
            keywords = yaml.load(f, Loader=yaml.FullLoader)
        ent_label = keyword_path.stem
        for concept_label, concept in keywords.items():
            concept_id = ";".join(concept["taxonomy_paths"]) + ";" + concept_label
            yield {
                "keywords": concept["keywords"],
                "label": ent_label,
                "id": concept_id,
                "concept_label": concept_label,
            }


def _build_keyword_patterns(
    nlp: Language, keyword_file_paths, pattern_f=lambda tok: {"lemma": tok.text.lower()}
):
    concepts_for_pipe = [
        (concept["keyword"], concept)
        for concept in get_keywords_from_yamls(keyword_file_paths)
    ]
    for doc, concept in tqdm(nlp.pipe(concepts_for_pipe, as_tuples=True)):
        yield {
            "pattern": [pattern_f(tok) for tok in doc],
            "label": concept["label"],
            "id": concept["id"],
        }


def create_concept_patterns(
    nlp: Language,
    out_path="assets/keywords_clean/patterns.jsonl",
    keyword_file_paths=KEYWORD_FILE_PATHS,
    case_sensitive=False,
):
    ruler = EntityRuler(nlp)
    patterns = _build_keyword_patterns(
        nlp,
        keyword_file_paths,
        lambda tok: {
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
        },
    )
    ruler.add_patterns(patterns)
    ruler.to_disk(out_path)
