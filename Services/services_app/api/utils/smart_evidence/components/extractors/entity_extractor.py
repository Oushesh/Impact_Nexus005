from typing import Any, List, Optional

import spacy
from spacy.language import Doc
from tqdm import tqdm

from app.models.annotation import (
    AnnotatedInsight,
    AnnotationType,
    Entity,
    EntityAnnotation,
    InsightAnnotation,
)
from smart_evidence.components.extractors.base_extractor import BaseExtractor
from smart_evidence.helpers.data import extract_entities


class EntityExtractor(BaseExtractor):
    """
    This node is used to extract entities out of documents.
    """

    def __init__(self, component, **data: Any):
        super().__init__(component, **data)
        if self.device >= 0:
            from thinc.api import require_gpu, set_gpu_allocator

            set_gpu_allocator("pytorch")
            require_gpu(self.device)
        self.nlp = spacy.load("en_ix_entity_ruler")
        self.nlp.add_pipe(
            "dbpedia_spotlight",
            config={
                # "dbpedia_rest_endpoint": "http://172.17.0.1:2222/rest",
                "overwrite_ents": False,
                "confidence": 0.35,
            },
        )

    def run(
        self, documents: List[AnnotatedInsight], **kwargs: Any
    ) -> List[AnnotatedInsight]:
        """
        This is the method called when this node is used in a pipeline
        """

        def content_generator(documents: List[AnnotatedInsight]):
            for document in documents:
                yield (document.text, document)

        annotated_documents = []
        for spacy_doc, document in self.nlp.pipe(
            tqdm(content_generator(documents)), as_tuples=True
        ):
            document = self.process(document, spacy_doc=spacy_doc)
            annotated_documents.append(document)

        return self.component.run(documents, **kwargs)

    def process(self, document: AnnotatedInsight, **kwds) -> AnnotatedInsight:
        entity_annotation = self(document.text, **kwds)
        annotation = InsightAnnotation.create_or_update_annotation(
            document,
            self.config.get("experiment_name", "test_experiment"),
            AnnotationType.machine,
            entities=entity_annotation,
        )
        document.add_annotation(annotation)
        return document

    def __call__(self, text: str, spacy_doc: Optional[Doc] = None) -> EntityAnnotation:
        if spacy_doc is None:
            spacy_doc = self.nlp(text)

        return EntityAnnotation.parse_obj(
            [Entity(**e) for e in extract_entities(spacy_doc)]
        )
