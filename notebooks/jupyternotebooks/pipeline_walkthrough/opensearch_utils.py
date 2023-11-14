from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
import os
#AWS_ACCESS_KEY_ID="AKIA5GMAAO24KANOAHJJ"
#AWS_SECRET_ACCESS_KEY="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"

# Create an index with non-default settings.
index_name = 'insights'
eval_index_name = 'evaluation_dev'

HOST = "search-ix-documents-rzvvmiarxdl7rnn47lj6ynnz4i.eu-central-1.es.amazonaws.com"
REGION = "eu-central-1"

AWS_AUTH = AWS4Auth(
    os.environ["AWS_ACCESS_KEY"],
    os.environ["AWS_SECRET_ACCESS_KEY"],
    REGION,
    "es",
)

client = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=AWS_AUTH,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

from smart_evidence.data_models.document_store_schema import INSIGHTS_MAPPING

#response = client.indices.create("eu-taxonomy-insights-dev-v5", body=INSIGHTS_MAPPING)



def get_query(size=100):
    query = {
              "size": size,
              "query": {
                "nested": {
                  "path": "annotations",
                  "query": {
                    "bool": {
                      "must": [
                        {
                          "term": {
                            "annotations.type": "HUMAN"
                          }
                        }
                      ]
                    }
                  }
                }
              }
            }
    return query 

def get_eval_query(size=100):
    query = {
              "size": size,
              "query": {'match_all' : {}
              }
            }
    return query 


def get_insight_filter_eval(filter_value, size=1000):
    query = {
      "size": size,
      "query": {
        "nested": {
          "path": "annotations",
          "query": {
            "bool": {
              "must": [
                {"term": {"annotations.tasks.content_control": f"{filter_value}"}}
              ]
            }
          }
        }
      }
    }
    return query 
