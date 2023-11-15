from haystack.document_stores import OpenSearchDocumentStore
from smart_evidence.helpers import opensearch_connection


# DocumentStore: holds all your data
document_store = OpenSearchDocumentStore(
    username="admin",
    password="R9$Cix3vD$BU#z",
    host=opensearch_connection.HOST,
    port=443,
    timeout=120,
    aws4auth=opensearch_connection.AWS_AUTH,
    verify_certs=True,
    index="paragraphs_v4",
    label_index="haystack-paragraphs-labels",
    search_fields=["text", "title"],
    embedding_field="embedding",
    similarity="cosine",
    excluded_meta_data=[
        "paragraphs",
    ],
    content_field="text",
    name_field="title",
)
