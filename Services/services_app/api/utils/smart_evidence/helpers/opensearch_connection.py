import os
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
import dotenv


dotenv.load_dotenv()

HOST = "search-ix-documents-rzvvmiarxdl7rnn47lj6ynnz4i.eu-central-1.es.amazonaws.com"
REGION = "eu-central-1"

AWS_AUTH = AWS4Auth(
    os.environ["AWS_ACCESS_KEY_ID"],
    os.environ["AWS_SECRET_ACCESS_KEY"],
    REGION,
    "es",
)

opensearch = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=AWS_AUTH,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)
