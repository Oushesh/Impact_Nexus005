import os
import validators

from haystack.utils import print_answers
from haystack.utils import fetch_archive_from_http, convert_files_to_docs, clean_wiki_text
from haystack.nodes import BM25Retriever, EmbeddingRetriever, FARMReader
from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import ExtractiveQAPipeline

class QARetrieval:
    def __init__(self,**kwargs):
        self.kwargs = kwargs

    @classmethod
    def initialize(cls,**kwargs):
        pass

    @classmethod
    def get_data(cls,url:str,output_dir:str):
        assert validators.url(url)==True
        #assert os.path.
        pass

if __name__ == "__main__":
    #QARetrieval.initialize()
    #QARetrieval.get_data()
    doc_dir = "data/tutorial11"
    os.makedirs(doc_dir,exist_ok=True)

    #Initialization Step:
    document_store = InMemoryDocumentStore(use_bm25=True)

    s3_url = "https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/wiki_gameofthrones_txt11.zip"
    fetch_archive_from_http(url=s3_url, output_dir=doc_dir)

    got_docs = convert_files_to_docs(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)
    document_store.delete_documents()
    document_store.write_documents(got_docs)

    bm25_retriever = BM25Retriever(document_store=document_store)

    embedding_retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    document_store.update_embeddings(embedding_retriever, update_existing_embeddings=False)

    # Initialize Reader
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2")

    p_extractive_premade = ExtractiveQAPipeline(reader=reader, retriever=bm25_retriever)
    res = p_extractive_premade.run(
        query="Who is the father of Arya Stark?", params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}
    )
    print_answers(res, details="minimum")

# TODO: redo this code with a series of steps needed:
# TODO: Make the data conform to DeepChecks classification (Train_test_split)



