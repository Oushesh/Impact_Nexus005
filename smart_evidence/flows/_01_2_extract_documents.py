from datetime import date
from pathlib import Path
from typing import Optional

import srsly
import typer
from haystack.document_stores import OpenSearchDocumentStore
from haystack.schema import Document
from smart_evidence.helpers import opensearch_connection
from smart_evidence.data_models.document_store_schema import DOCUMENTS_MAPPING
from tqdm import tqdm
from smart_evidence.components.filters import (
    DateFilter,
    LanguageFilter,
    RelevancyFilter,
    ImpactFilter,
)
from smart_evidence.components.classifiers.document_classifier import (
    HeuristicsDocumentClassifier,
)
from smart_evidence.components.processors.document_processor import DocumentProcessor
from smart_evidence.components import Component
from config_to_flow import get_flow


def run(
    input_folder: Path = Path("corpus/documents/"),
    index: str = "documents",
    filter_documents: bool = False,
    experiment: Optional[str] = None,
    config_path: Path = Path("smart_evidence/flows/configs/extract_documents.yaml"),
):
    """Extract document elements, e.g. paragraphs, abstracts from documents.

    Args:
        input_folder (Path, optional): Defaults to Path("corpus/documents/").
        index (str, optional): Defaults to "haystack-paragraphs".
    """
    ## define pipeline
    flow = eval(get_flow(config_path))

    # DocumentStore: holds all your data
    document_store: OpenSearchDocumentStore = OpenSearchDocumentStore(  # type: ignore
        username="admin",
        password="R9$Cix3vD$BU#z",
        host=opensearch_connection.HOST,
        port=443,
        timeout=60,
        aws4auth=opensearch_connection.AWS_AUTH,
        verify_certs=True,
        index=index,
        label_index="haystack-documents-labels",
        search_fields=["text", "title"],
        similarity="cosine",
        content_field="text",
        name_field="title",
        custom_mapping=DOCUMENTS_MAPPING,
        analyzer="english",
        duplicate_documents="skip",
    )

    n_documents = 0
    input_paths = list(Path(input_folder).glob("*.jsonl"))
    for input_path in sorted(input_paths):
        print(f"Uploading {input_path} to index {index}")
        items = srsly.read_jsonl(input_path)
        meta = {"source_file": input_path.stem}

        batch = []
        for document in flow.run(items, meta=meta):
            batch.append(document)

            if len(batch) >= 1_000:
                n_documents += len(batch)
                document_store.write_documents(
                    batch, batch_size=1_000, duplicate_documents="skip"
                )
                batch = []

        if len(batch):
            n_documents += len(batch)
            document_store.write_documents(
                batch, batch_size=1_000, duplicate_documents="skip"
            )
            batch = []
    print(f"Uploaded {n_documents} documents to elasticsearch.")


if __name__ == "__main__":
    typer.run(run)
