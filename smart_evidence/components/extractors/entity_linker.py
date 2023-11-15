import os
from typing import Any, List, Optional

from tqdm import tqdm

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    ConceptAnnotation,
    EntityAnnotation,
    InsightAnnotation,
)
from smart_evidence.components.extractors.base_extractor import BaseExtractor
from smart_evidence.helpers.concept_stores import (
    get_concepts,
)


class EntityLinker(BaseExtractor):
    """
    This node is used to link concepts with identified entities.
    """

    def __init__(self, component, **data: Any):
        super().__init__(component, **data)
        concepts = get_concepts()
        print(f"Number of company concepts to link with: {len(concepts)}")

        self.all_company_concepts = {}
        for concept in concepts:
            for dbpedia_id in concept.get("dbpedia_id", []) or []:
                self.all_company_concepts[dbpedia_id] = concept
            self.all_company_concepts[str(concept["id"])] = concept

        raise NotImplementedError("Implement linking impact concepts")
        # concepts = get_impact_concepts()
        print(f"Number of impact concepts to link with: {len(concepts)}")

        self.all_impact_concepts = {}
        for concept in concepts:
            for dbpedia_id in concept.get("dbpedia_id", []) or []:
                self.all_impact_concepts[dbpedia_id] = concept
            self.all_impact_concepts[str(concept["id"])] = concept

    def process(self, document: AnnotatedInsight, **kwds) -> Optional[AnnotatedInsight]:
        annotation = document.get_annotation_by(
            self.config.get("experiment_name", "test_experiment")
        )

        if not annotation or annotation.tasks.entities is None:
            print(f"Annotation not found {document.id}")
            return None

        concept_annotation = self(annotation.tasks.entities)
        annotation = InsightAnnotation.create_or_update_annotation(
            document,
            self.config.get("experiment_name", "test_experiment"),
            AnnotationType.machine,
            concepts=concept_annotation,
        )
        document.add_annotation(annotation)
        return document

    def __call__(self, entities: EntityAnnotation) -> ConceptAnnotation:
        impact_concepts = []
        company_concepts = []
        for entity in entities.__root__:
            if entity.label is None:
                continue

            if entity.label == "COMPANY" and entity.id in self.all_company_concepts:
                company_concepts.append(self.all_company_concepts[entity.id])
            if entity.label == "IMPACT" and entity.id in self.all_impact_concepts:
                impact_concepts.append(self.all_impact_concepts[entity.id])
            elif entity.label == "DBPEDIA_ENT" and entity.id is not None:
                kb_id = entity.id.split("/")[-1]
                if kb_id in self.all_company_concepts:
                    company_concepts.append(self.all_company_concepts[kb_id])
                elif kb_id in self.all_impact_concepts:
                    impact_concepts.append(self.all_impact_concepts[kb_id])

        impact_concepts = [
            concept
            for i, concept in enumerate(impact_concepts)
            if concept not in impact_concepts[:i]
        ]
        company_concepts = [
            concept
            for i, concept in enumerate(company_concepts)
            if concept not in company_concepts[:i]
        ]

        return ConceptAnnotation(
            impact_concepts=impact_concepts, company_concepts=company_concepts
        )

    def run(
        self,
        documents: List[Any],
        **kwds,
    ) -> List[Any]:

        processed_documents = []
        for document in tqdm(documents):
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)
