from typing import Any, Optional, List, Dict

import numpy as np
from tqdm import tqdm
from transformers import pipeline
from transformers.pipelines.zero_shot_classification import (
    ZeroShotClassificationPipeline,
)

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    ConceptAnnotation,
    ConceptRelation,
    InsightAnnotation,
    RelationAnnotation,
    create_placeholder_review,
)
from smart_evidence.components import BaseComponent, Component
from smart_evidence.components.classifiers.base_classifier import BaseClassifier
from smart_evidence.helpers.classifier_util import (
    _get_deduplicated_concept_pairs,
    _get_labels_with_groups,
    _results_to_predictions,
    BOOLQA_LABEL2PRED,
)
from smart_evidence.helpers.eval_util import run_evaluation


class PairedZeroShotClassificationPipeline(ZeroShotClassificationPipeline):
    def _sanitize_parameters(self, **kwargs):
        (
            preprocess_params,
            forward_params,
            postprocess_params,
        ) = super()._sanitize_parameters(**kwargs)
        if "label_groups" in kwargs:
            postprocess_params["label_groups"] = kwargs["label_groups"]
        return preprocess_params, forward_params, postprocess_params

    def postprocess(self, model_outputs, multi_label=False, label_groups=[]):
        candidate_labels = []
        sequences = []
        outputs = []
        for model_output in model_outputs:
            candidate_labels.append(model_output["candidate_label"])
            sequences.append(model_output["sequence"])
            outputs.append(model_output["logits"])

        if self.framework == "pt":
            if isinstance(outputs, list):
                logits = np.concatenate(
                    [output.cpu().numpy() for output in outputs], axis=0
                )
            else:
                logits = outputs["logits"].cpu().numpy()
        else:
            if isinstance(outputs, list):
                logits = np.concatenate([output.numpy() for output in outputs], axis=0)
            else:
                logits = outputs["logits"].numpy()

        N = logits.shape[0]
        n = len(candidate_labels)
        num_sequences = N // n
        reshaped_outputs = logits.reshape((num_sequences, n, -1))

        if multi_label or len(candidate_labels) == 1:
            # softmax over the entailment vs. contradiction dim for each label independently
            entailment_id = self.entailment_id
            contradiction_id = -1 if entailment_id == 0 else 0
            entail_contr_logits = reshaped_outputs[
                ..., [contradiction_id, entailment_id]
            ]
            scores = np.exp(entail_contr_logits) / np.exp(entail_contr_logits).sum(
                -1, keepdims=True
            )
            scores = scores[..., 1]
        elif label_groups:
            # softmax over label_groups per contradiction entailment logits
            entailment_id = self.entailment_id
            contradiction_id = -1 if entailment_id == 0 else 0
            entail_logits = reshaped_outputs[..., [contradiction_id, entailment_id]]
            label_groups = np.array(label_groups)
            scores = np.exp(entail_logits)
            group_ids = np.unique(label_groups)
            for i, group in enumerate(label_groups):
                scores[:, [i]] /= np.exp(
                    entail_logits[:, np.where(label_groups == group)[0]]
                ).sum(-2, keepdims=True)
        else:
            # softmax contradiction entailment logits per label
            entailment_id = self.entailment_id
            contradiction_id = -1 if entailment_id == 0 else 0
            entail_logits = reshaped_outputs[..., [contradiction_id, entailment_id]]
            label_groups = np.array(label_groups)
            scores = np.exp(entail_logits) / np.exp(entail_logits).sum(
                -1, keepdims=True
            )

        return {
            "sequence": sequences[0],
            "labels": candidate_labels,
            "scores": scores[0].tolist(),
            "groups": label_groups.tolist(),
        }


class CompanyImpactClassifier(BaseClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        if self.device < 0:
            self.model_name_or_path = "cross-encoder/nli-MiniLM2-L6-H768"
        else:
            self.model_name_or_path = data.get(
                "model_name_or_path", "cross-encoder/nli-MiniLM2-L6-H768"
            )
        self.pipeline = pipeline(
            model=self.model_name_or_path,
            pipeline_class=PairedZeroShotClassificationPipeline,
            device=self.device,
        )

    def process(self, document: AnnotatedInsight, **kwds) -> AnnotatedInsight:
        annotation = document.get_annotation_by(
            self.config.get("experiment_name", "default_experiment")
        )

        if annotation is None:
            return document

        relation_annotation = self(document.text, annotation.tasks.concepts)

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
        candidate_labels, label_groups, groups = _get_labels_with_groups(concept_pairs)
        try:
            result = self.pipeline(
                text,
                candidate_labels=candidate_labels,
                hypothesis_template="{}",
                label_groups=label_groups,
            )
        except RuntimeError:
            return RelationAnnotation.parse_obj([])

        return RelationAnnotation.parse_obj(
            [ConceptRelation(**ann) for ann in _results_to_predictions(result, groups)]
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
                    concepts: ConceptAnnotation = ConceptAnnotation(
                        company_concepts=[concept_relation.company_concept],
                        impact_concepts=[concept_relation.impact_concept],
                    )
                    prediction = (
                        self(document.text[:2000], concepts).__root__[0].relation.value
                    )
                    groundtruth.append(concept_relation.relation.value)
                    predictions.append(prediction)
        evaluations[type(self).__name__] = run_evaluation(
            groundtruth,
            predictions,
            list(BOOLQA_LABEL2PRED.keys()),
            self.evaluation_config,
        )
        evaluations[type(self).__name__]["labels"] = list(BOOLQA_LABEL2PRED.keys())
        return self.component.evaluate(documents, evaluations, **kwds)
