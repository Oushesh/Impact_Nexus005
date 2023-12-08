from haystack.pipelines import Pipeline
from haystack.nodes import Crawler, Preprocessor, BM25Retriever, FARMReader
from haystack_core_components.DocumentStores import DocumentStores

class Pipeline:
    def __init__(self,**kwargs):
        self.pipeline_object = Pipeline(**kwargs)

    @classmethod
    def build_pipeline(cls,component,component_name:str):
        assert isinstance(component_name,str)
        component_input_name = component_name + "_input"
        assert isinstance(component_input_name,str)
        self.pipeline_object.add_node(component=component, name=component_name,input=[component_input_name])

    @classmethod
    def run_pipeline(cls,pipeline_object):
        pipeline_object.run()

