from opensearchpy.helpers import reindex
from smart_evidence.helpers.opensearch_connection import opensearch as client
from smart_evidence.data_models.document_store_schema import (
    DOCUMENTS_MAPPING,
    INSIGHTS_MAPPING,
    CONCEPTS_MAPPING,
)

import srsly
import typer
from app.opensearch_migrations.scrape_mapping import SCRAPE_MAPPING
from enum import Enum

index_mappings = {
    "insights": INSIGHTS_MAPPING,
    "documents": DOCUMENTS_MAPPING,
    "scrape": SCRAPE_MAPPING,
    "concepts": CONCEPTS_MAPPING,
}


class IndexType(str, Enum):
    insights = "insights"
    documents = "documents"
    concepts = "concepts"
    scrape = "scrape"


def create_index(index, mapping):
    response = None
    try:
        response = client.indices.create(index, body=mapping)
    except Exception as e:
        response = e
    return response


def run(
    index_name: str = "documents-dev-1",
    index_type: IndexType = IndexType.documents,
):
    mapping = index_mappings.get(index_type)
    # create documents index
    print(
        f"{index_name} with type `{index_mappings}` index creation status: ",
        create_index(index=index_name, mapping=mapping),
    )


if __name__ == "__main__":
    typer.run(run)
