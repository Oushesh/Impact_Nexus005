import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
from opensearchpy.helpers import bulk, scan

from app.models.annotation import (
    AnnotatedInsight,
    SimpleConcept,
)  # pylint: disable=W0401,W0611
from app.models.documents import (  # pylint: disable=W0401,W0611
    AnnotatedDocument,
    Document,
    ScrapeItem,
)
from app.models.concepts import ConceptML
from app.models.impact_screening import Insight  # pylint: disable=W0401,W0611
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.data_stores.base_store import BaseStore
from smart_evidence.data_models.document_store_schema import *  # pylint: disable=W0401,W0614
from smart_evidence.helpers import opensearch_connection
from smart_evidence.helpers.errors import DocumentStoreError
from smart_evidence.helpers.filter_util import LogicalFilterClause

BASE_QUERY: Any = {"query": {"match_all": {}}}
HUMAN_QUERY = {
    "query": {
        "nested": {
            "path": "annotations",
            "query": {"term": {"annotations.type": "HUMAN"}},
        }
    }
}
SIMILARITY_SPACE_TYPE_MAPPINGS = {
    "nmslib": {"cosine": "cosinesimil", "dot_product": "innerproduct", "l2": "l2"},
    "faiss": {"cosine": "innerproduct", "dot_product": "innerproduct", "l2": "l2"},
}


class OpenSearchStore(BaseStore):
    def __init__(self, component: BaseComponent, **data):
        super().__init__(component, **data)
        self.os_client = opensearch_connection.opensearch
        self.batch_size = self.component_config.get("batch_size", 1_000)
        self.embedding_field = self.component_config.get("embedding_field", "embedding")
        self.similarity = self.component_config.get("similarity", "cosine")
        self.index = self.component_config["index"]
        self.document_class: Any = eval(  # pylint: disable=W0123
            self.component_config.get("document_class", "AnnotatedInsight")
        )
        if not self.os_client.indices.exists(index=self.index):
            self.index_mapping = eval(  # pylint: disable=W0123
                self.component_config["index_mapping"]
            )
            response = self.os_client.indices.create(
                index=self.index, body=self.index_mapping
            )
            logging.info(response)

    def _from_hit(self, hit):
        document = self.document_class(id=hit["_id"], **hit["_source"])
        return document

    def item_generator(self, **kwds):
        hit_generator = scan(
            self.os_client,
            query=kwds.get("query"),
            index=self.index,
            size=self.batch_size,
            scroll="1d",
        )

        document_generator = (self._from_hit(hit) for hit in hit_generator)
        return document_generator

    def write_batch(self, batch: List[Any]):
        def _docs_for_bulk(index, docs, overwrite=True):
            bulk_docs = []
            for doc in docs:
                doc_dict = {}
                if not isinstance(doc, dict):
                    if self.exclude_fields:
                        doc_dict = doc.dict(
                            exclude=set(self.exclude_fields), exclude_none=True
                        )
                    else:
                        doc_dict = doc.dict(exclude_none=True)
                else:
                    doc_dict = doc
                _id = doc_dict.pop("id")
                bulk_docs.append(
                    {
                        "_id": _id,
                        "_index": index,
                        "_op_type": "index" if overwrite else "create",
                        **doc_dict,
                    }
                )
            return bulk_docs

        try:
            return bulk(
                self.os_client,
                _docs_for_bulk(self.index, batch),
                request_timeout=60 * 5,
            )
        except Exception as e:
            print("Error in parsing a document:", e)
            return

    def query_by_embedding(
        self,
        query_emb: np.ndarray,
        filters: Optional[Dict[str, Union[Dict, List, str, int, float, bool]]] = None,
        top_k: int = 10,
        index: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Any]:
        """
        Find the document that is most similar to the provided `query_emb` by using a vector similarity metric.
        :param query_emb: Embedding of the query (e.g. gathered from DPR)
        :param filters: Optional filters to narrow down the search space to documents whose metadata fulfill certain
                        conditions.
                        Filters are defined as nested dictionaries. The keys of the dictionaries can be a logical
                        operator (`"$and"`, `"$or"`, `"$not"`), a comparison operator (`"$eq"`, `"$in"`, `"$gt"`,
                        `"$gte"`, `"$lt"`, `"$lte"`) or a metadata field name.
                        Logical operator keys take a dictionary of metadata field names and/or logical operators as
                        value. Metadata field names take a dictionary of comparison operators as value. Comparison
                        operator keys take a single value or (in case of `"$in"`) a list of values as value.
                        If no logical operator is provided, `"$and"` is used as default operation. If no comparison
                        operator is provided, `"$eq"` (or `"$in"` if the comparison value is a list) is used as default
                        operation.
                            __Example__:
                            ```python
                            filters = {
                                "$and": {
                                    "type": {"$eq": "article"},
                                    "date": {"$gte": "2015-01-01", "$lt": "2021-01-01"},
                                    "rating": {"$gte": 3},
                                    "$or": {
                                        "genre": {"$in": ["economy", "politics"]},
                                        "publisher": {"$eq": "nytimes"}
                                    }
                                }
                            }
                            # or simpler using default operators
                            filters = {
                                "type": "article",
                                "date": {"$gte": "2015-01-01", "$lt": "2021-01-01"},
                                "rating": {"$gte": 3},
                                "$or": {
                                    "genre": ["economy", "politics"],
                                    "publisher": "nytimes"
                                }
                            }
                            ```
                            To use the same logical operator multiple times on the same level, logical operators take
                            optionally a list of dictionaries as value.
                            __Example__:
                            ```python
                            filters = {
                                "$or": [
                                    {
                                        "$and": {
                                            "Type": "News Paper",
                                            "Date": {
                                                "$lt": "2019-01-01"
                                            }
                                        }
                                    },
                                    {
                                        "$and": {
                                            "Type": "Blog Post",
                                            "Date": {
                                                "$gte": "2019-01-01"
                                            }
                                        }
                                    }
                                ]
                            }
                            ```
        :param top_k: How many documents to return
        :param index: Index name for storing the docs and metadata
        :param headers: Custom HTTP headers to pass to elasticsearch client (e.g. {'Authorization': 'Basic YWRtaW46cm9vdA=='})
                Check out https://www.elastic.co/guide/en/elasticsearch/reference/current/http-clients.html for more information.
        :return:
        """
        if index is None:
            index = self.index

        if not self.embedding_field:
            raise DocumentStoreError(
                "Please set a valid `embedding_field` for OpenSearchDocumentStore"
            )
        # +1 in similarity to avoid negative numbers (for cosine sim)
        if not filters:
            filters = {"match_all": {}}
        body: Dict[str, Any] = {
            "size": top_k,
            "query": self._get_vector_similarity_query(query_emb, top_k, filters),  # type: ignore
        }
        if filters:
            filter_ = LogicalFilterClause.parse(filters).convert_to_elasticsearch()
            if "script_score" in body["query"]:
                # set filter for pre-filtering (see https://opensearch.org/docs/latest/search-plugins/knn/knn-score-script/)
                body["query"]["script_score"]["query"] = {"bool": {"filter": filter_}}
            else:
                body["query"]["bool"]["filter"] = filter_

        result = self.os_client.search(
            index=index, body=body, request_timeout=60 * 5, headers=headers
        )["hits"]["hits"]

        documents = []
        for hit in result:
            score = hit["_score"]
            hit["_source"]["similarity_score"] = np.round(1 / (1 + np.exp(-score)), 2)  # type: ignore
            documents.append(self._from_hit(hit))
        return documents

    def _get_vector_similarity_query(
        self, query_emb: np.ndarray, top_k: int, filters: dict = {"match_all": {}}
    ):
        """
        Generate Elasticsearch query for vector similarity.
        """
        if not isinstance(query_emb, list):
            query_emb = query_emb.tolist()
        query = {
            "script_score": {
                "query": filters,
                "script": {
                    "source": "knn_score",
                    "lang": "knn",
                    "params": {
                        "field": self.embedding_field,
                        "query_value": query_emb,
                        "space_type": SIMILARITY_SPACE_TYPE_MAPPINGS["nmslib"][
                            self.similarity
                        ],
                    },
                },
            }
        }
        return query
