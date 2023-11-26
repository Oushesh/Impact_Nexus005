import logging
from typing import Any, List, Optional

from tqdm import tqdm
from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    InsightAnnotation,
    SimpleConcept,
)
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.extractors.base_extractor import BaseExtractor
from smart_evidence.models.concept_extractor import ConceptExtractor


class CompanyConceptExtractor(BaseExtractor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.model = ConceptExtractor(**data)

    def process(self, document: Any, **kwds) -> Optional[AnnotatedInsight]:
        annotation = document.get_annotation_by(
            self.config.get("experiment_name", "test_experiment")
        )

        if annotation is None:
            logging.info(f"New annotation for {document.id}")
            annotation = InsightAnnotation(
                type=AnnotationType.machine,
                created_by=self.config.get("experiment_name", "test_experiment"),
            )

        company_concepts = [
            SimpleConcept(label=c, id=None)
            for c in self.model(getattr(document, self.content_field), **kwds)
        ]
        if annotation.tasks.concepts is not None:
            company_concepts = list(
                set(annotation.tasks.concepts.company_concepts + company_concepts)
            )
        annotation.tasks.concepts.company_concepts = company_concepts

        document.add_annotation(annotation)
        return document

    def run(
        self,
        documents: List[Any],
        **kwds,
    ) -> List[Any]:

        processed_documents = []
        for document in tqdm(documents, desc="CompanyConceptExtractor"):
            processed_document = self.process(document, **kwds)
            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)
