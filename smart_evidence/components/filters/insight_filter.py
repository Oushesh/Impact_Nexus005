from typing import Any, List, Union

from app.models.annotation import AnnotatedInsight
from smart_evidence.components import BaseComponent, Component
from smart_evidence.components.classifiers.insight_classifier import InsightClassifier
from smart_evidence.components.filters.base_filter import BaseFilter


class InsightFilter(BaseFilter):
    def __init__(self, component: BaseComponent, **data: Any):
        self._component = component
        super().__init__(component, **data)
        self.insight_classifier = InsightClassifier(Component(), **data)

    def process(
        self, document: AnnotatedInsight, **kwds
    ) -> Union[bool, AnnotatedInsight]:
        document = self.insight_classifier.process(document)  # type: ignore
        if not document:
            return False
        annotation = document.get_annotation_by(
            self.config.get("experiment_name", "default_experiment")
        )
        return annotation is not None and annotation.tasks.content_control == "FEATURED"

    def run(
        self, documents: List[AnnotatedInsight], **kwargs,
    ) -> List[AnnotatedInsight]:
        filtered_documents: List[AnnotatedInsight] = []
        for document in documents:
            if self.process(document, **kwargs):
                filtered_documents.append(document)

        return self.component.run(filtered_documents, **kwargs,)
