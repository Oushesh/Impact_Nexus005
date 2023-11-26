import logging
from typing import List, Any
from app.models.documents import Document
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.base_classifier import BaseClassifier


class HeuristicsDocumentClassifier(BaseClassifier):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

    def process(self, document: Document, **kwds) -> Document:
        label = "OTHER"
        scraper = getattr(document, "scraper")
        if scraper in [
            "cambridge-core-sdg",
            "wuppertal",
            "pik",
            "oeko",
        ]:
            label = "RESEARCH"
        elif scraper in ["iea", "eea", "ipcc", "oecd", "ILO"]:
            label = "REPORT"
        elif scraper in ["eur-lex"]:
            label = "REGULATION"
        elif scraper in ["hypothesis"]:
            label = "NEWS_BLOGS"
        elif scraper in ["wikipedia"]:
            label = "WIKIPEDIA"

        document.document_source = label

        return document

    def run(self, documents: List[Document], **kwargs: Any) -> List[Document]:
        processed_documents: List[Document] = []
        for document in documents:
            processed_documents.append(self.process(document=document))

        return self.component.run(processed_documents, **kwargs)
