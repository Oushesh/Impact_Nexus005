import logging
from typing import Any, Dict, List, Optional
from tqdm import tqdm
from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    ConceptAnnotation,
    ConceptRelation,
    InsightAnnotation,
    RelationAnnotation,
    create_placeholder_review,
)
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.base_classifier import BaseClassifier
from smart_evidence.helpers.classifier_util import (
    _get_deduplicated_concept_pairs,
    _get_qa_style_text_pairs,
    _boolqa_results_to_predictions,
    BOOLQA_PRED2LABEL,
    BOOLQA_LABEL2PRED,
)
from smart_evidence.helpers.eval_util import run_evaluation
from sentence_transformers.cross_encoder import CrossEncoder


logger = logging.getLogger(__name__)


class BoolQACompanyImpactClassifier(BaseClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

        self.pipeline = CrossEncoder(self.model_name_or_path)

    def process(self, document: AnnotatedInsight, **kwds) -> AnnotatedInsight:
        annotation = document.get_annotation_by(
            self.config.get("experiment_name", "default_experiment")
        )

        if annotation is None:
            return document

        relation_annotation = self(document.text, annotation.tasks.concepts)  # type: ignore

        annotation = InsightAnnotation.create_or_update_annotation(
            document,
            self.config.get("experiment_name", "default_experiment"),
            AnnotationType.machine,
            relations=relation_annotation,
        )

        document.add_annotation(annotation)
        return document

    def __call__(self, text: str, concepts: ConceptAnnotation) -> RelationAnnotation:
        # Log if token length of document is longer than model's max input tokens.
        text = text[:2000]
        company_concepts = concepts.company_concepts
        impact_concepts = concepts.impact_concepts

        if not company_concepts or not impact_concepts:
            return RelationAnnotation.parse_obj([])

        concept_pairs = _get_deduplicated_concept_pairs(
            company_concepts, impact_concepts
        )
        text_concept_pairs = _get_qa_style_text_pairs(concept_pairs, text)
        try:
            result = self.pipeline.predict(text_concept_pairs)
        except RuntimeError:
            return RelationAnnotation.parse_obj([])

        return RelationAnnotation.parse_obj(
            [
                ConceptRelation(**ann)
                for ann in _boolqa_results_to_predictions(concept_pairs, result)
            ]
        )

    def run(self, documents: List[Any], **kwds,) -> List[Any]:

        processed_documents = []
        for document in tqdm(documents):
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)

    def evaluate(
        self, documents: List[AnnotatedInsight], evaluations: Dict, **kwds
    ) -> Dict:
        groundtruth: List = []
        predictions: List = []
        for document in documents:
            annotation = create_placeholder_review(document.get_human_annotations())
            if annotation.tasks.relations:
                for concept_relation in annotation.tasks.relations.__root__:
                    text_concept_pairs = _get_qa_style_text_pairs(
                        [
                            (
                                concept_relation.company_concept,
                                concept_relation.impact_concept,
                            )
                        ],
                        document.text[:2000],
                    )
                    prediction: int = self.pipeline.predict(text_concept_pairs).argmax()  # type: ignore
                    groundtruth.append(concept_relation.relation.value)
                    predictions.append(BOOLQA_PRED2LABEL[prediction])
        evaluations[type(self).__name__] = run_evaluation(
            groundtruth,
            predictions,
            list(BOOLQA_LABEL2PRED.keys()),
            self.evaluation_config,
        )
        evaluations[type(self).__name__]["labels"] = list(BOOLQA_LABEL2PRED.keys())
        return self.component.evaluate(documents, evaluations, **kwds)
