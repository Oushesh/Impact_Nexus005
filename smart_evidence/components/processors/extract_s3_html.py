import json
import logging
from typing import Any, List, Optional

import boto3
from smart_evidence.helpers.processor_util import html_extraction_to_document
from trafilatura.core import extract

from app.models.documents import Document, ScrapeItem
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor


class ExtractHTML(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.s3 = boto3.resource("s3")

    def process(self, document: ScrapeItem, **kwds) -> Optional[Document]:
        s3_obj = self.s3.Object(
            "ix-nexus", document.storage_url.split("s3://ix-nexus/")[-1]
        )
        content = s3_obj.get()["Body"].read().decode("utf-8")

        extracted_document = document.dict()
        extraction = extract(content, url=document.url, output_format="json")
        extracted_document = html_extraction_to_document(
            extracted_document=extracted_document,
            extraction=extraction,
            document=document,
        )
        return Document(**extracted_document)

    def run(self, documents: List[Any], **kwds):
        processed_documents = []
        for document in documents:
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)
        return self.component.run(processed_documents, **kwds)
