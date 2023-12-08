from haystack.pipelines import Pipeline
from haystack.nodes import Crawler, PreProcessor, BM25Retriever, FARMReader

from haystack_core_components.DocumentStores import DocumentStore

crawler = Crawler(
    urls=["https://haystack.deepset.ai"],   # Websites to crawl
    crawler_depth=1,    # How many links to follow
    output_dir="crawled_files",  # The directory to store the crawled files, not very important, we don't use the files in this example
)

class Crawler_Pipeline:
    def __init__(self,**kwargs):
        self.kwargs = kwargs


