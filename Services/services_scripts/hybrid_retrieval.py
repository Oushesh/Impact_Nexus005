"""
Desgin the Haystack pipeline
in a way its easy to integrate
with testing on DVC type and Django endpoints so far.
"""

from datasets import load_dataset
from haystack.document_stores import InMemoryDocumentStore
from haystack.schema import Document
import json
from haystack.nodes import PreProcessor

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
    def transform_data(cls,dataset,schema:Document):
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
    def build_preprocessor(cls, preprocessing_configs):
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
    def data_schema(cls):
        pass


documents=HybridRetrieval_Pipeline.get_data("ywchoi/pubmed_abstract_3")
preprocessing_configs = {
            "clean_empty_lines":True,
            "clean_whitespace":True,
            "clean_header_footer":True,
            "split_by":"word",
            "split_length":512,
            "split_overlap":32,
            "split_respect_sentence_boundary":True,
        }


preprocessor=HybridRetrieval_Pipeline.build_preprocessor(preprocessing_configs)
HybridRetrieval_Pipeline.preprocess(preprocessor,documents)
