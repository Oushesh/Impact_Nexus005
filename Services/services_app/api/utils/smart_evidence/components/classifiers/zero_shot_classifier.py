from typing import Any, List
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.base_classifier import BaseClassifier
from transformers.pipelines import pipeline
from transformers.pipelines.zero_shot_classification import (
    ZeroShotClassificationPipeline,
)


class ZeroShotClassifier(BaseClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

        self.pipeline = pipeline(
            model=self.model_name_or_path,
            pipeline_class=ZeroShotClassificationPipeline,
            device=self.device,
            task="text-classification",
        )

    def process(self, document: Any, **kwds) -> Any:
        raise NotImplementedError

    def run(
        self,
        documents: List[Any],
        **kwds,
    ) -> List[Any]:
        raise NotImplementedError
