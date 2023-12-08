import os
import json
import logging
from google.cloud import storage
from ninja import Router
from pathlib import Path

from haystack.nodes import Crawler, BM25Retriever,FARMReader
from haystack.nodes import PreProcessor
from haystack import BaseComponent
from typing import List
from services_app.haystack_core_components.DocumentStores import DocumentStore
from services_app.haystack_core_components.pipeline_builder import BuildPipeline


router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configure logging
logging.basicConfig(level=logging.INFO, filename=os.path.join(BASE_DIR,"logs/haystack_cralwer.log"), filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


logger = logging.getLogger(__name__)

class HaystackCrawler(BaseComponent):
    outgoing_edges = 1
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def run(self,input:str):
        pass

    def run_batch(self,batch_input:List[str]):
        pass

    @classmethod
    def configure_DocumentStore(cls, document_store: str):
        assert isinstance(document_store, str)
        assert document_store in ["InMemory", "Elasticsearch", "FAISS", "Milvus", "OpenSearch", "Pinecone", "Qdrant",
                                  "Weaviate"]
        return DocumentStore.load_DocumentStore(document_store)

    @classmethod
    def build_crawler(cls, urls: List[str], crawler_depth: int, output_dir: str):
        assert isinstance(crawler_depth, int)
        assert isinstance(output_dir, str)
        os.makedirs(output_dir, exist_ok=True)
        return Crawler(urls, crawler_depth, output_dir)

    @classmethod
    def build_preprocessor(cls, preprocessing_configs):
        preprocessor = PreProcessor(
            clean_empty_lines=preprocessing_configs["clean_empty_lines"],
            clean_whitespace=preprocessing_configs["clean_whitespace"],
            clean_header_footer=preprocessing_configs["clean_header_footer"],
            split_by=preprocessing_configs["split_by"],
            split_length=preprocessing_configs["split_length"],
            split_respect_sentence_boundary=preprocessing_configs["split_respect_sentence_boundary"]
        )
        return preprocessor

#TODO: convert the cralwer into an endpoint here.

@router.get("/crawler")
def haystack_crawler(request):
    return {"data":"success"}