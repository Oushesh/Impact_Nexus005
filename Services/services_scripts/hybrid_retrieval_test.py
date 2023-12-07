from datasets import load_dataset
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import EmbeddingRetriever, BM25Retriever
from haystack.schema import Document
from typing import List, Optional,Dict

"""
dataset = load_dataset("ywchoi/pubmed_abstract_3", split="test")

document_store = InMemoryDocumentStore(use_bm25=True, embedding_dim=384)



documents = []
for doc in dataset:
    documents.append(
        Document(
            content=doc["title"] + " " + doc["text"],
            meta={"title": doc["title"], "abstract": doc["text"], "pmid": doc["pmid"]},
        )
    )


from haystack.nodes import PreProcessor

preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=512,
    split_overlap=32,
    split_respect_sentence_boundary=True,
)

docs_to_index = preprocessor.process(documents)


sparse_retriever = BM25Retriever(document_store=document_store)
dense_retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    use_gpu=False,
    scale_score=False,
)

document_store.delete_documents()
document_store.write_documents(docs_to_index)
document_store.update_embeddings(retriever=dense_retriever)

"""

## TODO:  Rewrite this pipeline as class with the hybrid_retrieval

class HybridRetrieval_Pipeline:
    def __init__(self,**kwargs):
        self.kwargs = kwargs


    @classmethod
    def get_data(cls,url:str,type="test",location="local"):
        assert location in ["local","s3","gs"]
        if location == "local":
            dataset = load_dataset(url,type)
        elif location == "s3":
            dataset = "None"
            pass
            #TODo: add the method to read in data here from boto3
        elif location == "gs":
            dataset  = "None"
            pass
            #TODO: add the method to sync data from google cloud bucket like
            #TODO: we did for the endpoints.
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


if __name__ == "__main__":
    url = "ywchoi/pubmed_abstract_3"
    documents = HybridRetrieval_Pipeline.get_data(url)
    schema = {"title","text"."pmid"}
    #TODO: test the schema
    documents_transformed = HybridRetrieval_Pipeline.transform_data(documents)

#TODO: write about testing this with DVC then endpoint then production


