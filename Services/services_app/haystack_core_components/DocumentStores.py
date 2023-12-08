class DocumentStore:
    def __init__(self,doc_store:str):
        assert doc_store in ["InMemory","ElasticSearch","Milvus","OpenSearch","Pinecone","Qdrant","SQL","Weaviate","FAISS"]
        self.doc_store = doc_store

    @classmethod
    def load_DocumentStore(self,doc_store:str):
        if doc_store == "InMemory":
            from haystack.document_stores import InMemoryDocumentStore
            return InMemoryDocumentStore(use_bm25=True, embedding_dim=384)
        elif doc_store == "ElasticSearch":
            from haystack.document_stores import ElasticsearchDocumentStore
            return ElasticsearchDocumentStore()
        elif doc_store == "Milvus":
            from haystack import Document
            try:
                from milvus_documentstore import MilvusDocumentStore
                return MilvusDocumentStore()
            except ImportError as e:
                print(f"Error importing MilvusDocumentStore: {e}")
                print("MilvusDocumentStore is not available. Please install it using the following command:")
                print(
                    "pip install -e \"git+https://github.com/deepset-ai/haystack-extras.git#egg=milvus_documentstore&subdirectory=stores/milvus-documentstore\"")

        elif doc_store == "OpenSearch":
            from haystack.document_stores import OpenSearchDocumentStore
            return OpenSearchDocumentStore()

        elif doc_store == "Pinecone":
            from haystack.document_stores import PineconeDocumentStore
            return PineconeDocumentStore(
                    api_key='YOUR_API_KEY',
                    similarity="cosine",
                    index='your_index_name',
                    embedding_dim=768
                )
        elif doc_store == "Qdrant":
            from qdrant_haystack.document_stores import QdrantDocumentStore
            return QdrantDocumentStore(
                ":memory:",
                index="Document",
                embedding_dim=512,
                recreate_index=True,
                hnsw_config={"m": 16, "ef_construct": 64}  # Optional
                )

        elif doc_store == "SQL":
            from haystack.document_stores import SQLDocumentStore
            return SQLDocumentStore()

        elif doc_store == "Weaviate":
            from haystack.document_stores import WeaviateDocumentStore
            return WeaviateDocumentStore()
        elif doc_store == "FAISS":
            from haystack.document_stores import FAISSDocumentStore
            return FAISSDocumentStore()
        else:
            raise ValueError (f"unknown DocumentStore")



