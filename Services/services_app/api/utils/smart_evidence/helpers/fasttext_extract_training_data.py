"""
Exracts paragraphs and concepts from Opensearch and writes to different files,
Datasets are in the input format of fasttext,
_paragraphs: one paragraph per line,
_concepts: Concept labels that are normalized to be single word,
only replaced WHITESPACE with _, e.g. Carbon emissions ⇒ Carbon_emissions
"""

from pathlib import Path

from haystack.document_stores import OpenSearchDocumentStore

from smart_evidence.helpers import opensearch_connection
from smart_evidence.data_models.document_store_schema import INSIGHTS_MAPPING
import typer
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_document_store(index):
    document_store = OpenSearchDocumentStore(
        username="admin",
        password="R9$Cix3vD$BU#z",
        host=opensearch_connection.HOST,
        port=443,
        timeout=60,
        aws4auth=opensearch_connection.AWS_AUTH,
        verify_certs=True,
        index=index,
        label_index="haystack-paragraphs-labels",
        search_fields=["text", "title"],
        similarity="cosine",
        content_field="text",
        name_field="title",
        custom_mapping=INSIGHTS_MAPPING,
        analyzer="english",
        duplicate_documents="overwrite",
    )
    return document_store


def get_documents(document_store, index: str):
    return document_store.get_all_documents_generator(index=index)


def extract_data(
    index: str = "haystack-paragraphs",
    file_name: str = "knowledge_base_paragraphs",
    output_folder: Path = Path("fastText/data"),
):
    paragraphs_file_path = output_folder / Path(file_name)
    concepts_file_path = output_folder / Path(file_name + "_concepts")

    paragraphs_file = open(paragraphs_file_path, "w")
    concepts_file = open(concepts_file_path, "w")

    document_store = get_document_store(index)
    documents = get_documents(document_store, index)

    count = 0
    error_count = 0
    for doc in documents:
        try:
            paragraphs_file.write(doc.content)
            paragraphs_file.write("\n")

            concepts = [
                concept.replace(" ", "_") for concept in doc.meta.get("concepts")
            ]
            concepts_line = " ".join(concept for concept in concepts)
            concepts_file.write(concepts_line)
            concepts_file.write("\n")
            count += 1
            if count % 35000 == 0:
                logging.info("Current Paragraph Count: " + str(count))
        except Exception:
            error_count += 1
            continue

    paragraphs_file.close()
    concepts_file.close()

    logging.info("Total Paragraphs: ", str(count))
    logging.warning("Total Errors: ", str(error_count))


if __name__ == "__main__":
    typer.run(extract_data)
