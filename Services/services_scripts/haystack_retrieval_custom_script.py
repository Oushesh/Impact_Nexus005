import os

import validators
from haystack.pipelines import ExtractiveQAPipeline, DocumentSearchPipeline
from haystack.utils import print_answers
from haystack.utils import fetch_archive_from_http, convert_files_to_docs, clean_wiki_text

from haystack.nodes import BM25Retriever, EmbeddingRetriever, FARMReader
from haystack.utils import fetch_archive_from_http, convert_files_to_docs

from haystack.document_stores import InMemoryDocumentStore

from haystack.pipelines import ExtractiveQAPipeline

class QARetrieval:
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def initialize(cls,**kwargs):
        pass


    @classmethod
    def get_data(cls,url:str):
        pass


if __name__ == "__main__":
    #QARetrieval.initialize()
    #QARetrieval.get_data()
    output_dir = "data/tutorial11"
    os.makedirs(output_dir,exist_ok=True)

    #Initialization Step:
    document_store = InMemoryDocumentStore(use_bm25=True)
    bm25_retriever = BM25Retriever()

    got_docs = convert_files_to_docs(dir_path=output_dir,clean_func=clean_wiki_text,split_paragraphs=True)

    document_store.delete_documents()
    document_store.write_docs(got_docs)

    p_retrieval = DocumentSearchPipeline(bm25_retriever)

    bm25_retriever = BM25Retriever(document_store=document_store)

    #Add option to change the model name here
    embedding_retriever = EmbeddingRetriever(document_store = document_store, embedding_model = "sentence-transformers/multi-qa-mpnet-base-dot-v1")


    #Model name or path
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")

    p_extractive_premade = ExtractiveQAPipeline(reader=reader, retriever=bm25_retriever)

    res = p_extractive_premade.run(query = "Who is the father of Arya Stark?", params = {"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}})



# TODO: redo this code with a series of steps needed:
# TODO: Make the data conform to DeepChecks classification (Train_test_split)



