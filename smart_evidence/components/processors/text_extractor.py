from typing import Any, List, Optional

from app.models.documents import Document, ScrapeItem
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor
from smart_evidence.components.processors.extract_s3_html import ExtractHTML
from smart_evidence.components.processors.extract_pdf import ExtractPDF


class TextExtractor(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.extractors = {}
        for document_type, extractor in self.component_config.get(
            "extractors", {}
        ).items():
            self.extractors[document_type] = eval(f"{extractor}(component, **data)")

    def process(self, document: ScrapeItem, **kwds) -> Optional[Document]:
        extracted_document = None
        extracted_document = self.extractors[document.type].process(document)
        return extracted_document

    def run(self, documents: List[Any], **kwds):
        processed_documents = []
        for document in documents:
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)
        return self.component.run(processed_documents, **kwds)
