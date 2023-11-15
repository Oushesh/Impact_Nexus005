from opensearchpy.helpers import reindex
from smart_evidence.helpers.opensearch_connection import opensearch as client
from smart_evidence.data_models.document_store_schema import (
    DOCUMENTS_MAPPING,
    INSIGHTS_MAPPING,
)


INSIGHTS_MAPPING

SOURCE_INDEX = "insights"
NEW_INDEX = "insights_v2"

client.indices.create(index=NEW_INDEX, body=INSIGHTS_MAPPING)
reindex(client, SOURCE_INDEX, NEW_INDEX)

SOURCE_INDEX = "documents"
NEW_INDEX = "documents_v2"

client.indices.create(index=NEW_INDEX, body=DOCUMENTS_MAPPING)
reindex(client, SOURCE_INDEX, NEW_INDEX)
