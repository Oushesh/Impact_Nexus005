import logging
from typing import Any, Dict, List

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    ConceptAnnotation,
    InsightAnnotation,
    SimpleConcept,
)
from Services.services_app.rest_api import InsightForConcept
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.zero_shot_classifier import (
    ZeroShotClassifier,
)
from smart_evidence.flows.config_to_flow import get_flow

logger = logging.getLogger(__name__)


class ESGRelatedInsightsClassifier(ZeroShotClassifier):
    def process(self, document: InsightForConcept, **kwds) -> InsightForConcept:  # type: ignore
        prediction: Dict = self.pipeline(
            getattr(document, self.content_field),
            candidate_labels=[document.concept],  # type: ignore
            hypothesis_template="The organization is {}",
        )
        if "scores" in prediction:
            document.confidence_score = round(prediction["scores"][0], 2)
        return document

    def run(
        self,
        documents: List[InsightForConcept],
        **kwds,
    ) -> List[InsightForConcept]:

        processed_documents = []
        for document in documents:
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)


class ESGRelatedConceptsClassifier(ZeroShotClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

        self.concept_datastore = eval(
            get_flow(self.component_config.get("concept_datastore", {}), is_file=False)
        )
        self.prompt = self.component_config.get("prompt", "")
        self.nli_threshold = self.component_config.get("nli_threshold")
        self.top_k = self.component_config.get("top_k")
        self.similarity_threshold = self.component_config.get(
            "similarity_threshold", 0.0
        )
        self.filters = self.concept_datastore.component_config.get("filters")

    def process(self, document: AnnotatedInsight, **kwds) -> AnnotatedInsight:
        concepts: List = kwds.get("concepts", [])
        labels: List = [getattr(concept, "label") for concept in concepts]
        if labels is None:
            return document

        prediction: Dict = self.pipeline(
            getattr(document, self.content_field),
            candidate_labels=labels,  # type: ignore
            hypothesis_template=self.prompt,
        )
        if "scores" in prediction:
            for score, concept in zip(prediction["scores"], prediction["labels"]):
                if score >= self.nli_threshold:
                    annotation = document.get_annotation_by(
                        self.config.get("experiment_name", "test_experiment")
                    )

                    if annotation is None:
                        annotation = InsightAnnotation(
                            type=AnnotationType.machine,
                            created_by=self.config.get(
                                "experiment_name", "test_experiment"
                            ),
                        )
                    company_concepts = [
                        SimpleConcept(
                            label=concepts[labels.index(concept)].label,
                            id=concepts[labels.index(concept)].id,
                            similarity_score=concepts[
                                labels.index(concept)
                            ].similarity_score,
                        )
                    ]
                    if annotation.tasks.concepts is None:
                        annotation.tasks.concepts = ConceptAnnotation(
                            company_concepts=company_concepts
                        )
                    else:
                        for concept in company_concepts:
                            if (
                                concept
                                not in annotation.tasks.concepts.company_concepts
                            ):
                                annotation.tasks.concepts.company_concepts.append(
                                    concept
                                )

                    document.add_annotation(annotation)
        return document

    def run(
        self,
        documents: List[AnnotatedInsight],
        **kwds,
    ) -> List[AnnotatedInsight]:

        processed_documents = []
        for document in documents:
            assert document.embedding is not None, "document must be embedded."
            # retrieve top_k hits with cosine similarity over embeddings
            concepts = self.concept_datastore.query_by_embedding(
                query_emb=document.embedding, filters=self.filters, top_k=self.top_k
            )
            filtered_concepts = list(
                filter(
                    lambda concept: (
                        concept.similarity_score >= self.similarity_threshold
                    ),
                    concepts,
                )
            )
            if len(filtered_concepts):
                document = self.process(document, concepts=filtered_concepts)
            processed_documents.append(document)

        return self.component.run(processed_documents, **kwds)
