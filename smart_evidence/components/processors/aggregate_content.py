import json
import logging
from typing import Any, List, Optional, Union

from app.models.documents import Document
from app.models.annotation import AnnotatedInsight
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor


class AggregateContent(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.aggregation_fields: List[str] = self.component_config.get(
            "aggregation_fields", []
        )
        assert (
            len(self.aggregation_fields) > 1
        ), "There should atleast two aggregation fields"
        self.aggregation_delimeter: str = self.component_config.get(
            "aggregation_delimeter", " "
        )

    def process(
        self, document: Union[Document, AnnotatedInsight], **kwds
    ) -> Optional[Union[Document, AnnotatedInsight]]:
        content = f"{self.aggregation_delimeter}".join(
            [
                getattr(document, aggregation_field)
                for aggregation_field in self.aggregation_fields
            ]
        )
        setattr(document, self.content_field, content)
        return document

    def run(self, documents: List[Any], **kwds):
        processed_documents = []
        for document in documents:
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)
        return self.component.run(processed_documents, **kwds)
