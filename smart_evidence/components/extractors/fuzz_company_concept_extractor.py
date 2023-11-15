import logging
from pydoc import doc
from typing import Any, List, Optional

import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from thefuzz import fuzz
from tqdm import tqdm

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    InsightAnnotation,
    SimpleConcept,
)
from smart_evidence.components import BaseComponent
from smart_evidence.components.extractors.base_extractor import BaseExtractor
from smart_evidence.models.fuzz_concept_extractor import FuzzConceptExtractor
from smart_evidence.helpers.concept_stores import (
    get_concepts,
)


class FuzzCompanyConceptExtractor(BaseExtractor):
    # A list of concepts should be given at the initialization.
    # An example of concepts_list is ['cement', 'greenhouse gas', 'limestone']
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        company_concepts = get_concepts()
        self.model = FuzzConceptExtractor([c["label"] for c in company_concepts])

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
        for document in tqdm(documents, desc="FuzzCompanyConceptExtractor"):
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)
