from datasets import load_dataset
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever, BM25Retriever
from haystack.schema import Document
from typing import List, Optional,Dict
from haystack.nodes import PreProcessor

from haystack_core_components.DocumentStores import DocumentStore

class HybridRetrieval_Pipeline:
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def configure_DocumentStore(cls,document_store:str):
        assert isinstance(document_store,str)
        assert document_store in ["InMemory","Elasticsearch","FAISS","Milvus","OpenSearch","Pinecone","Qdrant","Weaviate"]
        return DocumentStore.load_DocumentStore(document_store)

    @classmethod
    def get_data(cls,url:str,split="test",location="local"):
        assert location in ["local","s3","gs"]
        assert split in ["train","test","validation"]

        if location == "local":
            dataset = load_dataset(url,split="test")

        elif location == "s3":
            dataset = "None"
            pass
            #TODO: add the method to read in data here from boto3

        elif location == "gs":
            dataset  = "None"
            pass
            #TODO: add the method to sync data from google cloud bucket like
            #TODO: we did for the endpoints
        return dataset

    @classmethod
    def transform_data(cls,dataset,schema:Dict):
        documents = []
        for doc in dataset:
            documents.append(
                Document(
                    content=doc["title"] + " " + doc["text"],
                    meta={"title": doc["title"], "abstract": doc["text"], "pmid": doc["pmid"]},
                )
            )
        return documents

    @classmethod
    def preprocess(cls,preprocessor,documents):
        return preprocessor.process(documents)


    @classmethod
    def build_preprocessor(cls,preprocessing_configs):
        preprocessor = PreProcessor(
            clean_empty_lines=preprocessing_configs["clean_empty_lines"],
            clean_whitespace=preprocessing_configs["clean_whitespace"],
            clean_header_footer=preprocessing_configs["clean_header_footer"],
            split_by=preprocessing_configs["split_by"],
            split_length=preprocessing_configs["split_length"],
            split_overlap=preprocessing_configs["split_overlap"],
            split_respect_sentence_boundary=preprocessing_configs["split_respect_sentence_boundary"],
        )
        return preprocessor

    @classmethod
    def build_retriever(cls,retriever_type:str,document_store):
        assert isinstance(retriever_type,str)
        assert retriever_type in ["dense_retriever","sparse_retriever"]

        if retriever_type == "dense_retriever":
            dense_retriever = EmbeddingRetriever(
                document_store=document_store,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2",
                use_gpu=False,
                scale_score=False,
            )
            return dense_retriever
        elif retriever_type == "sparse_retriever":
            return BM25Retriever(document_store=document_store)
        else:
            raise ValueError("Unknown retriever type")
        return preprocessor


if __name__ == "__main__":
    url = "ywchoi/pubmed_abstract_3"
    dataset = HybridRetrieval_Pipeline.get_data(url)
    print (dataset)
    schema = {"title","text","pmid"}
    #TODO: test the schema
    documents_transformed = HybridRetrieval_Pipeline.transform_data(dataset,schema)

    document_store = HybridRetrieval_Pipeline.configure_DocumentStore("InMemory")

    preprocessing_configs = {
            "clean_empty_lines":True,
            "clean_whitespace":True,
            "clean_header_footer":True,
            "split_by":"word",
            "split_length":512,
            "split_overlap":32,
            "split_respect_sentence_boundary":True,
    }

    preprocessor = HybridRetrieval_Pipeline.build_preprocessor(preprocessing_configs)
    docs_to_index = HybridRetrieval_Pipeline.preprocess(preprocessor,documents_transformed)

    document_store.delete_documents()
    document_store.write_documents(docs_to_index)

    document_store.update_embeddings(retriever=HybridRetrieval_Pipeline.build_retriever("dense_retriever",document_store))

#Ref: https://docs.haystack.deepset.ai/docs/document_store

