from haystack.pipelines import Pipeline
from typing import List


class BuildPipeline:
    def __init__(self):
        self.pipeline = Pipeline()

    def add_node(self, component, name, inputs):
        self.pipeline.add_node(component=component, name=name, inputs=inputs)

    def run_pipeline(self):
        self.pipeline.run()


