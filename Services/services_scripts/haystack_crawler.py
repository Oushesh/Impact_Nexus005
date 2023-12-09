from haystack.nodes import Crawler,BM25Retriever, FARMReader
from haystack.nodes import PreProcessor
from haystack import BaseComponent
from typing import List
from haystack_core_components.DocumentStores import DocumentStore

import os
from haystack_core_components.pipeline_builder import BuildPipeline

class Crawler_Pipeline(BaseComponent):
    outgoing_edges = 1
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self,input:str):
        pass

    def run_batch(self, batch_input:List[str]):
        pass

    @classmethod
    def configure_DocumentStore(cls,document_store:str):
        assert isinstance(document_store, str)
        assert document_store in ["InMemory", "Elasticsearch", "FAISS", "Milvus", "OpenSearch", "Pinecone", "Qdrant",
                                  "Weaviate"]
        return DocumentStore.load_DocumentStore(document_store)

    @classmethod
    def build_crawler(cls,urls:List[str],crawler_depth:int,output_dir:str):
        assert isinstance(crawler_depth,int)
        assert isinstance(output_dir,str)
        os.makedirs(output_dir, exist_ok=True)
        return Crawler(urls, crawler_depth, output_dir)

    @classmethod
    def build_preprocessor(cls,preprocessing_configs):
        preprocessor = PreProcessor(
            clean_empty_lines=preprocessing_configs["clean_empty_lines"],
            clean_whitespace=preprocessing_configs["clean_whitespace"],
            clean_header_footer=preprocessing_configs["clean_header_footer"],
            split_by=preprocessing_configs["split_by"],
            split_length=preprocessing_configs["split_length"],
            split_respect_sentence_boundary=preprocessing_configs["split_respect_sentence_boundary"]
        )
        return preprocessor

if __name__ == "__main__":
    preprocessing_configs = {
        "clean_empty_lines": True,
        "clean_whitespace": True,
        "clean_header_footer": False,
        "split_by": "word",
        "split_length": 500,
        "split_respect_sentence_boundary": True
    }
    pipeline = Crawler_Pipeline()
    preprocessor = pipeline.build_preprocessor(preprocessing_configs=preprocessing_configs)

    urls = ["https://haystack.deepset.ai"]
    crawler_depth = 1
    output_dir = "crawled_files"

    crawler = Crawler_Pipeline.build_crawler(urls, crawler_depth=crawler_depth,output_dir=output_dir)

    indexing_pipeline = BuildPipeline()
    # Add nodes to build the pipeline
    indexing_pipeline.add_node(component=crawler, name="crawler", inputs=['File'])
    indexing_pipeline.add_node(component=preprocessor, name="preprocessor", inputs=['crawler'])
    document_store = Crawler_Pipeline.configure_DocumentStore("InMemory")

    indexing_pipeline.add_node(component=document_store, name="document_store", inputs=['preprocessor'])

    indexing_pipeline.run_pipeline()

    retriever = BM25Retriever(document_store=document_store)
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2-distilled")

    query_pipeline = BuildPipeline()
    query_pipeline.add_node(component=retriever, name="retriever", inputs=['Query'])
    query_pipeline.add_node(component=reader,name="reader", inputs=['retriever'])

    results = query_pipeline.run_pipeline(query="What can I use haystack for?")
    print("\nQuestion: ", results["query"])
    print("\nAnswers:")
    for answer in results["answers"]:
        print("- ", answer.answer)
    print("\n\n")
