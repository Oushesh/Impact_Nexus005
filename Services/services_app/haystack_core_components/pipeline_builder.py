from haystack.pipelines import Pipeline
from typing import List, Optional

class BuildPipeline:
    def __init__(self):
        self.pipeline = Pipeline()

    def add_node(self, component, name, inputs):
        self.pipeline.add_node(component=component, name=name, inputs=inputs)

    def run_pipeline(self,query:Optional[str]=None):
        self.pipeline.run(query=query)


