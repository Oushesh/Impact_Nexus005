import logging
from typing import Any, Dict, List, Union

from setfit import SetFitModel

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    InsightAnnotation,
    create_placeholder_review,
)
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.base_classifier import BaseClassifier
from smart_evidence.helpers.classifier_util import (
    INSIGHT_CLASSIFIER_LABEL2PRED,
    INSIGHT_CLASSIFIER_PRED2LABEL,
)
from smart_evidence.helpers.eval_util import run_evaluation

logger = logging.getLogger(__name__)


class InsightClassifier(BaseClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.model = SetFitModel.from_pretrained(self.model_name_or_path)

    def process(  # type: ignore
        self, document: AnnotatedInsight, **kwds
    ) -> Union[bool, AnnotatedInsight]:
        content = getattr(document, self.content_field)

        if content is None:
            return False
        label = self.model([content])[0]
        annotation = InsightAnnotation.create_or_update_annotation(
            document,
            self.config.get("experiment_name", "default_experiment"),
            AnnotationType.machine,
            content_control=INSIGHT_CLASSIFIER_PRED2LABEL[label],
        )
        document.add_annotation(annotation)
        return document

    def run(
        self, documents: List[AnnotatedInsight], **kwargs: Any
    ) -> List[AnnotatedInsight]:
        processed_documents = []
        for document in documents:
            anotation = self.process(document=document)
            if anotation:
                processed_documents.append(anotation)
        return self.component.run(processed_documents, **kwargs)

    def evaluate(
        self, documents: List[AnnotatedInsight], evaluations: Dict, **kwds
    ) -> Dict:
        groundtruth: List = []
        predictions: List = []
        for document in documents:
            content = getattr(document, self.content_field)
            prediction = INSIGHT_CLASSIFIER_PRED2LABEL[self.model([content])[0]]
            annotation = create_placeholder_review(document.get_human_annotations())
            if annotation.tasks.content_control:
                groundtruth.append(
                    "HIDDEN"
                    if annotation.tasks.content_control == "HIDDEN"
                    else "FEATURED"
                )
                predictions.append(prediction)

        evaluations[type(self).__name__] = run_evaluation(
            groundtruth,
            predictions,
            list(INSIGHT_CLASSIFIER_PRED2LABEL.values()),
            self.evaluation_config,
            labels_map=INSIGHT_CLASSIFIER_LABEL2PRED,
        )
        evaluations[type(self).__name__]["labels"] = list(
            INSIGHT_CLASSIFIER_PRED2LABEL.values()
        )
        return self.component.evaluate(documents, evaluations, **kwds)
