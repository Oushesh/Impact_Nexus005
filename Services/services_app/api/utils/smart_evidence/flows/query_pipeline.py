from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer
from haystack.nodes import ElasticsearchRetriever
from haystack.schema import Document

from haystack.pipelines import Pipeline
from sklearn.cluster import AgglomerativeClustering, Birch
from sklearn.cluster import DBSCAN
from smart_evidence.components.count_clustering import CountClustering
from smart_evidence.components.count_transformers_clustering import (
    CountTransformerClustering,
)
from smart_evidence.components.document_classifier import HeuristicsDocumentClassifier
from smart_evidence.components.summarizer import IXTransformersSummarizer
from smart_evidence.components.transformers_clustering import TransformersClustering
from smart_evidence.flows.document_stores import document_store


class FilterRetriever(ElasticsearchRetriever):
    """
    Naive "Retriever" that returns all documents that match the given filters. No impact of query at all.
    Helpful for benchmarking, testing and if you want to do QA on small documents without an "active" retriever.
    """

    def retrieve(
        self,
        query: Optional[str],
        filters: List[str] = None,
        top_k: Optional[int] = None,
        custom_query: Optional[str] = None,
        index: str = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Document]:
        """
        Scan through documents in DocumentStore and return a small number documents
        that are most relevant to the query.
        :param query: Has no effect, can pass in empty string
        :param filters: A dictionary where the keys specify a metadata field and the value is a list of accepted values for that field
        :param top_k: Has no effect, pass in any int or None
        :param index: The name of the index in the DocumentStore from which to retrieve documents
        :param headers: Custom HTTP headers to pass to elasticsearch client (e.g. {'Authorization': 'Basic YWRtaW46cm9vdA=='})
                Check out https://www.elastic.co/guide/en/elasticsearch/reference/current/http-clients.html for more information.
        :param scale_score: Whether to scale the similarity score to the unit interval (range of [0,1]).
                                           If true similarity scores (e.g. cosine or dot_product) which naturally have a different value range will be scaled to a range of [0,1], where 1 means extremely relevant.
                                           Otherwise raw similarity scores (e.g. cosine or dot_product) will be used.
        """
        if index is None:
            index = self.document_store.index

        body = {
            "size": 5000,
            "query": {
                "bool": {
                    "should": [
                        # TODO filters should be a list!!
                        {"match_phrase": {field: value}}
                        for field, values in filters.items()
                        for value in values
                    ]
                }
            },
        }

        result = self.document_store.client.search(index=index, body=body)["hits"][
            "hits"
        ]

        documents = [
            self.document_store._convert_es_hit_to_document(
                hit, return_embedding=self.document_store.return_embedding
            )
            for hit in result
        ]

        return documents


# Retriever: A Fast and simple algo to identify the most promising candidate documents
retriever = FilterRetriever(document_store, top_k=5000)
document_classifier = HeuristicsDocumentClassifier()
# extractor = EntityExtractor()
# classifier = CompanyImpactClassifier()

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
count_transformer_clustering = CountTransformerClustering(
    embedder=embedder, eps=0.3, min_samples=2, metric="cosine"
)
# clustering = CountClustering()
# summarizer = IXTransformersSummarizer("sshleifer/distilbart-xsum-12-6")
summarizer = IXTransformersSummarizer("chinhon/headline_writer")

count_transformer_cluster_pipeline = Pipeline()
count_transformer_cluster_pipeline.add_node(
    component=retriever, name="Retriever", inputs=["Query"]
)
count_transformer_cluster_pipeline.add_node(
    component=document_classifier, name="DocumentClassifier", inputs=["Retriever"]
)
# pipeline.add_node(
#     component=extractor, name="EntityExtractor", inputs=["DocumentClassifier"]
# )
# pipeline.add_node(
#     component=classifier,
#     name="CompanyImpactClassifier",
#     inputs=["EntityExtractor"],
# )
count_transformer_cluster_pipeline.add_node(
    component=count_transformer_clustering,
    name="Clustering",
    inputs=["DocumentClassifier"],
)
count_transformer_cluster_pipeline.add_node(
    component=summarizer, name="Summarizer", inputs=["Clustering"]
)

count_clustering = CountClustering(min_cluster_size=2)

count_cluster_pipeline = Pipeline()
count_cluster_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
count_cluster_pipeline.add_node(
    component=document_classifier, name="DocumentClassifier", inputs=["Retriever"]
)
count_cluster_pipeline.add_node(
    component=count_clustering, name="Clustering", inputs=["DocumentClassifier"]
)
count_cluster_pipeline.add_node(
    component=summarizer, name="Summarizer", inputs=["Clustering"]
)

final_clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.6)
# clustering = DBSCAN(eps=0.3, min_samples=2, metric="cosine")
clustering = Birch(threshold=0.5, n_clusters=final_clustering)
transformer_clustering = TransformersClustering(
    clustering=clustering,
    min_cluster_size=2,
    embedder=embedder,
)

transformer_cluster_pipeline = Pipeline()
transformer_cluster_pipeline.add_node(
    component=retriever, name="Retriever", inputs=["Query"]
)
transformer_cluster_pipeline.add_node(
    component=document_classifier, name="DocumentClassifier", inputs=["Retriever"]
)
transformer_cluster_pipeline.add_node(
    component=transformer_clustering, name="Clustering", inputs=["DocumentClassifier"]
)
transformer_cluster_pipeline.add_node(
    component=summarizer, name="Summarizer", inputs=["Clustering"]
)

plain_pipeline = Pipeline()
plain_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])


pipelines = {
    "plain_pipeline": plain_pipeline,
    "count_transformer_cluster_pipeline": count_transformer_cluster_pipeline,
    "count_cluster_pipeline": count_cluster_pipeline,
    "transformer_cluster_pipeline": transformer_cluster_pipeline,
}
