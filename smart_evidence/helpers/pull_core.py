from pathlib import Path
from typing import Optional
import requests

import pickle
import pandas as pd
import srsly
from glob import glob
import re
import numpy as np
from time import sleep

from tqdm import tqdm


def create_cooccurance_df(file_path: Optional[Path] = None) -> pd.DataFrame:
    if not file_path:
        file_path = sorted(glob("cooccurance_*.pickle"))[-1]
    with open(file_path, "br") as f:
        company_vocabulary, impact_vocabulary, cooccurrence_matrix_sparse = pickle.load(
            f
        )

    df = pd.DataFrame(
        cooccurrence_matrix_sparse,
        index=company_vocabulary.keys(),
        columns=impact_vocabulary.keys(),
    )

    columns = list(df.columns)
    for id in columns:
        if id.count(";") > 1:
            parts = id.split(";")
            concept_label = parts[-1]
            taxonomies = parts[:-1]
            for taxonomy in taxonomies:
                df[f"{taxonomy};{concept_label}"] = df[id]
            df = df.drop(columns=id)

    indices = list(df.index)
    for id in indices:
        if id.count(";") > 1:
            parts = id.split(";")
            concept_label = parts[-1]
            taxonomies = parts[:-1]
            for taxonomy in taxonomies:
                df.loc[f"{taxonomy};{concept_label}"] = df.loc[id]
            df = df.drop(index=id)

    def turn_string_to_multi(index):
        parts = re.split("[\|\/]", index)
        indices = []
        for part in parts:
            if len(parts) != 6 and part in ["COMPANY"]:
                indices += [""] * (6 - len(parts))
            indices.append(part.strip())
        return tuple(indices)

    df.columns = pd.MultiIndex.from_tuples(
        [re.split(r"[\|\/]", col) for col in df.columns]
    )

    df.index = pd.MultiIndex.from_tuples(
        [turn_string_to_multi(ind) for ind in df.index]
    )

    df = df.iloc[:, np.argsort(-df.sum(0).values)]

    return df


df = create_cooccurance_df()


def core_to_doc(core_doc):
    doc = {
        "title": core_doc.pop("title"),
        "text": core_doc.pop("fullText"),
        "abstract": core_doc.pop("abstract"),
        "scraper": "core",
    }

    urls = core_doc.pop("sourceFulltextUrls")
    if urls:
        doc["url"] = urls[0]
    else:
        doc["url"] = core_doc["downloadUrl"]

    doc["meta"] = core_doc
    return doc


# def generate_docs(df):
#     for column in tqdm(df.columns):
#         impact_concept = column[-1].split(";")[-1]
#         company_concepts = set()
#         for index, value in tqdm(
#             df.loc[:, column].sort_values().dropna().iteritems(), desc=impact_concept
#         ):
#             if value < 5:
#                 continue
#             company_concept = [p for p in index if not pd.isna(p)][-2].split(";")[-1]
#             if company_concept not in company_concepts:
#                 company_concepts.add(company_concept)
#                 params = {
#                     "limit": 1000,
#                     "q": f"abstract:({company_concept}) AND abstract:({impact_concept})",
#                 }
#                 response = requests.get(
#                     "https://api.core.ac.uk/v3/search/works",
#                     params=params,
#                     timeout=60,
#                     headers={
#                         "Authorization": "Bearer y7zX5xtrFTsJw2PVkaYONDZjUKEM9B4u"
#                     },
#                 )
#                 if not response:
#                     if response.status_code == 429:
#                         sleep(6 * 60)
#                     continue

#                 try:
#                     result = response.json()
#                     for doc in result["results"]:
#                         yield core_to_doc(doc)
#                 except:
#                     continue


PAGE_SIZE = 50

session = requests.Session()


def get_pages(params):
    page_offset = 0
    while page_offset < 1001:
        params["offset"] = page_offset

        response = session.post(
            "https://api.core.ac.uk/v3/search/works",
            body=params,
            timeout=60,
            headers={"Authorization": "Bearer y7zX5xtrFTsJw2PVkaYONDZjUKEM9B4u"},
        )
        if not response:
            if response.status_code == 429:
                sleep(6 * 60)
                continue
            print(response, response.content)
            continue
        else:
            page_offset += PAGE_SIZE
            yield response


def generate_docs(df):
    for impact_concept in tqdm(
        (
            item["concept_label"]
            for item in get_concepts_from_yamls(["assets/keywords_clean/IMPACT.yaml"])
        )
    ):
        params = {
            "q": f"abstract:({impact_concept})",
            "limit": PAGE_SIZE,
            "exclude": ["references", "data_provider", "contributors", "authors"],
        }
        for response in get_pages(params):
            try:
                result = response.json()
                for doc in result["results"]:
                    yield core_to_doc(doc)
            except Exception as e:
                print("Response couldn't be parsed:", e)
                continue


from smart_evidence.helpers.concept_patterns import get_concepts_from_yamls

srsly.write_jsonl("core_impacts2.jsonl", generate_docs(df))
