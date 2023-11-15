import json
import logging
from typing import Any, Dict, List, Optional
import uuid

from trafilatura import extract, fetch_url
from trafilatura.settings import use_config

from app.models.documents import Document, DocumentType
from rest_api.schema import EUTaxonomyClassificationRequest
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor
from smart_evidence.helpers.processor_util import html_extraction_to_document


class ExtractScraperHTML(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        config = use_config()
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
        self._trafilatura_config = config

    def process(self, url: Any, **kwds) -> Optional[Document]:
        processed_document = None
        try:
            extracted_document: Dict = {}
            scraped_document = fetch_url(url)
            extraction = extract(
                scraped_document, output_format="json", config=self._trafilatura_config
            )
            extracted_document = html_extraction_to_document(
                extracted_document=extracted_document,
                extraction=extraction,
                url=url,
            )
            processed_document = Document(
                **extracted_document,
                _id=uuid.uuid4().hex,
                storage_url=url,
                type=DocumentType.html,
                venture_id=kwds.get("venture_id", ""),
                scraper=self.config.get("experiment_name", "eu-taxonomy"),
            )
        except:
            pass
        return processed_document

    def run(self, documents: Any, **kwds):
        processed_documents = []
        urls = documents.urls
        venture_id = documents.venture_id
        for document in urls:
            processed_document = self.process(document, venture_id=venture_id)
            if processed_document is not None:
                processed_documents.append(processed_document)
        return self.component.run(processed_documents, **kwds)
