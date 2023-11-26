from datetime import datetime
from typing import Optional
from smart_evidence.helpers.data import hash_documents
from smart_evidence.components.processors.base_processor import BaseProcessor
from smart_evidence.components import BaseComponent
from typing import Any, List
from collections import defaultdict
from app.models.documents import Document

SOURCE_TO_TEXT_FIELD = defaultdict(lambda: "text")
SOURCE_TO_TEXT_FIELD["core"] = "abstract"


class DocumentProcessor(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

    def run(self, documents: List[Any], **kwargs) -> List[Any]:
        processed_documents = []
        for item in documents:
            if item.get("text") is None:
                item["text"] = ""

            meta = kwargs.get("meta", {"meta": {}})
            item = {"created_at": datetime.now(), **meta, **item}
            item = {"metadata": item.pop("meta"), **item}
            item = {
                "content_field": SOURCE_TO_TEXT_FIELD[item.get("scraper")],
                **item,
            }
            processed_documents.append(item)
        processed_documents = hash_documents(processed_documents, id_field="id")
        processed_documents = [Document(**document) for document in processed_documents]

        return self.component.run(processed_documents, **kwargs)
