import logging
import re
from typing import Any, List, Optional

from smart_evidence.components import BaseComponent
from smart_evidence.components.filters.base_filter import BaseFilter


class DateFilter(BaseFilter):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

    def process(self, document: Any, **kwds) -> Optional[Any]:
        item_date = None
        date_pattern = re.compile(r"\b\d{4}\b")
        if "date" in document and document["date"]:
            item_date = date_pattern.search(document["date"])
        if item_date is None and "title" in document and document["title"]:
            item_date = date_pattern.search(document["title"])

        if item_date is not None and int(item_date.group(0)) < 2015:
            logging.info(
                f"Document with title and date is filtered out by date filter:",
                document["title"],
                document["date"],
            )
            return None
        return document

    def run(self, documents: List[Any], **kwargs) -> List[Any]:
        filtered_documents: List[Any] = []

        for document in documents:
            if self.process(document=document):
                filtered_documents.append(document)

        return self.component.run(filtered_documents, **kwargs)
