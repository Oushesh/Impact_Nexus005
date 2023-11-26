import logging
from typing import Any, List, Optional

import spacy
from spacy.matcher import PhraseMatcher

from smart_evidence.components import BaseComponent
from smart_evidence.components.filters.base_filter import BaseFilter
from smart_evidence.helpers.concept_patterns import get_keywords_from_yamls


class ImpactFilter(BaseFilter):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self._configure_impact_filter()

    def _configure_impact_filter(self):
        self.nlp = spacy.blank("en")
        self.nlp.max_length = 5000000
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        impact_keywords = [
            keyword["keyword"].lower()
            for keyword in get_keywords_from_yamls(
                [
                    "assets/keywords_clean/IMPACT.yaml",
                ]
            )
            if len(keyword["keyword"]) > 5
        ]
        patterns = [self.nlp.make_doc(text) for text in impact_keywords]
        self.matcher.add("ImpactConcepts", patterns)

    def process(self, document: Any, **kwds) -> Optional[Any]:
        doc = kwds.get("doc", None)
        if self.matcher(doc):
            return document
        else:
            logging.info(f"Document is filtered by impact concept filter:", doc)
            return None

    def run(self, documents: List[Any], **kwargs) -> List[Any]:
        filtered_documents: List[Any] = []
        for doc, document in self.nlp.pipe(
            (
                (
                    document.get(document.get("content_field", "text"), "") or "",
                    document,
                )
                for document in documents
            ),
            as_tuples=True,
        ):
            if self.process(document=document, doc=doc):
                filtered_documents.append(document)

        return self.component.run(filtered_documents, **kwargs)
