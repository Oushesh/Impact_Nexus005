import logging
from typing import Any, List, Optional

import pycld2 as cld2

from smart_evidence.components import BaseComponent
from smart_evidence.components.filters.base_filter import BaseFilter


class LanguageFilter(BaseFilter):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

    def process(self, document: Any, **kwds) -> Optional[Any]:
        content = getattr(document, self.content_field)
        try:
            item_lang = cld2.detect(content or "", hintLanguage="en")[2][0][1]
        except cld2.error:
            return None

        if item_lang == "en":
            return document
        else:
            logging.info(
                f"Document with text is filtered out by language filter:",
                content,
            )
            return None

    def run(self, documents: List[Any], **kwargs) -> List[Any]:
        filtered_documents: List[Any] = []
        for document in documents:
            if self.process(document=document):
                filtered_documents.append(document)

        return self.component.run(filtered_documents, **kwargs)
