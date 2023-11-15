import csv
from dataclasses import dataclass
from pathlib import Path
import re

import typer
from typing import Dict, List
import yaml
from datetime import date
from smart_evidence.helpers.opensearch_connection import opensearch
from opensearchpy.helpers import bulk


CONCEPT_TYPES = ["COMPANY", "IMPACT", "BANLIST"]

KEYWORD_GLOBS = [
    "**/BANLIST.tsv",
    "Impact/IRIS/**/IMPACT.tsv",
    "Products & Activities/**/COMPANY.tsv",
    "Products & Activities/**/IMPACT.tsv",
    "Products & Activities/**/BANLIST.tsv",
]

TRANSLATIONS = {"de": ["assets/keywords_raw/construction-products_en-de.tsv"]}

ES_INDEX_NAME = "concepts"

ES_MAPPING = {
    "mappings": {
        "properties": {
            "created_at": {"type": "date"},
            "concept_label": {"type": "text"},
            "type": {"type": "keyword"},
            "keywords": {
                "properties": {
                    "en": {"type": "text", "analyzer": "english"},
                    "de": {"type": "text", "analyzer": "german"},
                }
            },
            "taxonomy_paths": {"type": "keyword"},
        },
    },
}


@dataclass
class ConceptEntry:
    keywords: Dict[str, List]
    taxonomy_paths: List[str]


def _get_concept_entry(keywords, taxonomy_path):
    return {
        "keywords": {"en": sorted(keywords)},
        "taxonomy_paths": [taxonomy_path],
    }


def _update_concept_entry(concept_entry, keywords, taxonomy_path):
    for keyword in keywords:
        if keyword not in concept_entry["keywords"]["en"]:
            concept_entry["keywords"]["en"].append(keyword)

    concept_entry["keywords"]["en"].sort()

    if taxonomy_path not in concept_entry["taxonomy_paths"]:
        concept_entry["taxonomy_paths"].append(taxonomy_path)

    concept_entry["taxonomy_paths"].sort()


def _update_concept_entry_translations(concept_entry, keyword_translations):
    for keyword in concept_entry["keywords"]["en"]:
        for lang, keyword_translations_for_lang in keyword_translations.items():
            if (
                keyword.lower() in keyword_translations_for_lang
                and keyword_translations_for_lang[keyword.lower()]
                not in concept_entry.get(lang, [])
            ):
                if lang not in concept_entry["keywords"]:
                    concept_entry["keywords"][lang] = []
                concept_entry["keywords"][lang].append(
                    keyword_translations_for_lang[keyword.lower()]
                )
                concept_entry["keywords"][lang] = sorted(
                    list(set(concept_entry["keywords"][lang]))
                )


def _create_elastic_search_document(concept_type, concept_label, concept_entry):
    return {
        "_index": ES_INDEX_NAME,
        "_type": "_doc",
        "_source": {
            **concept_entry,
            "created_at": date.today(),
            "concept_label": concept_label,
            "type": concept_type,
        },
    }


def cleanup(
    input_path: Path = Path("assets/keywords_raw/"),
    output_path: Path = Path("assets/keywords_clean/"),
):

    if opensearch.indices.exists(ES_INDEX_NAME):
        opensearch.indices.delete(index=ES_INDEX_NAME)
    opensearch.indices.create(index=ES_INDEX_NAME, body=ES_MAPPING)

    keyword_dict: Dict[str, Dict[str, ConceptEntry]] = dict()
    for concept_type in CONCEPT_TYPES:
        keyword_dict[concept_type] = dict()

    keyword_paths = set(
        [
            Path(keyword_path)
            for keyword_glob in KEYWORD_GLOBS
            for keyword_path in input_path.glob(keyword_glob)
        ]
    )

    keyword_translations: Dict[str, Dict[str, str]] = {}
    for lang, file_paths in TRANSLATIONS.items():
        keyword_translations[lang] = {}
        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as tsvfile:
                spamreader = csv.reader(tsvfile, delimiter="\t")
                for row in spamreader:
                    keyword_translations[lang][row[0].lower()] = row[1]

    for keyword_path in keyword_paths:
        if re.search(r"\.deactivate(?:$|/)", str(keyword_path)):
            continue

        concept_type = keyword_path.stem
        if concept_type not in CONCEPT_TYPES:
            continue

        with open(keyword_path) as f_in:
            taxonomy_path = str(keyword_path.relative_to(input_path))[: -len(".tsv")]
            for line_number, line in enumerate(f_in, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if re.search("  +", line):
                    print(
                        f"Multiple spaces in {keyword_path} at line {line_number}: {line}"
                    )
                keywords = [
                    keyword.strip()
                    for keyword in re.split(r"\t+", line)
                    if keyword.strip()
                ]
                label = keywords[0][0].upper() + keywords[0][1:]

                if label in keyword_dict[concept_type]:
                    concept_entry = keyword_dict[concept_type][label]
                    _update_concept_entry(concept_entry, keywords, taxonomy_path)
                else:
                    concept_entry = _get_concept_entry(keywords, taxonomy_path)
                    keyword_dict[concept_type][label] = concept_entry
                _update_concept_entry_translations(concept_entry, keyword_translations)

            if concept_type == "COMPANY":
                for label in taxonomy_path.split("/")[2:-1]:
                    label = label.split("_")[-1]
                    keywords = [label]
                    if label in keyword_dict[concept_type]:
                        concept_entry = keyword_dict[concept_type][label]
                        _update_concept_entry(concept_entry, keywords, taxonomy_path)
                    else:
                        concept_entry = _get_concept_entry(keywords, taxonomy_path)
                        keyword_dict[concept_type][label] = concept_entry
                    _update_concept_entry_translations(
                        concept_entry, keyword_translations
                    )

    for concept_type in CONCEPT_TYPES:
        concept_documents = [
            _create_elastic_search_document(concept_type, concept_label, concept_entry)
            for concept_label, concept_entry in keyword_dict[concept_type].items()
        ]
        bulk(opensearch, concept_documents)
        output_path.mkdir(exist_ok=True, parents=True)
        output_filepath = output_path / f"{concept_type}.yaml"
        print(f"{len(keyword_dict[concept_type])} {concept_type} > {output_filepath}")
        with open(output_filepath, "w") as f_out:
            yaml.dump(keyword_dict[concept_type], f_out, sort_keys=True)


if __name__ == "__main__":
    typer.run(cleanup)
