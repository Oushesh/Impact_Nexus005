import typer
from haystack.document_stores import OpenSearchDocumentStore
from smart_evidence.helpers import opensearch_connection
from haystack.nodes import EmbeddingRetriever

from smart_evidence.data_models.document_store_schema import INSIGHTS_MAPPING

# from smart_evidence.nodes.company_impact_classifier import (
#     CompanyImpactClassifier,
# )


# DocumentStore: holds all your data
document_store = OpenSearchDocumentStore(
    username="admin",
    password="R9$Cix3vD$BU#z",
    host=opensearch_connection.HOST,
    port=443,
    timeout=60,
    aws4auth=opensearch_connection.AWS_AUTH,
    verify_certs=True,
    index="haystack-paragraphs",
    label_index="haystack-paragraphs-labels",
    search_fields=["text", "title"],
    similarity="cosine",
    content_field="text",
    name_field="title",
    custom_mapping=INSIGHTS_MAPPING,
    analyzer="english",
    duplicate_documents="overwrite",
)

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/all-mpnet-base-v2",
    model_format="sentence_transformers",
)


def run_pipeline():
    document_store.update_embeddings(retriever, update_existing_embeddings=False)


if __name__ == "__main__":
    typer.run(run_pipeline)
