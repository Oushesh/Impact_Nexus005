import re
from typing import Any, List, Optional

from smart_evidence.components import BaseComponent
from smart_evidence.components.filters.base_filter import BaseFilter


class RelevancyFilter(BaseFilter):
    def process(self, document: Any, **kwds) -> Optional[Any]:
        content = getattr(document, self.content_field)
        only_chars = re.compile(r"[\d\W]+")
        has_old_date = re.compile(
            r"(\b1\d\d\d\b|(20th|19th|18th|17th).*(century|centuries|ct))"
        )
        has_new_date = re.compile(r"(\b2\d\d\d\b|(21st).*(century|centuries|ct))")

        if not content or len(only_chars.sub("", content)) < 100:
            return None

        # Filter out contents talking about the past
        if has_old_date.search(content.lower(),) and not has_new_date.search(
            content.lower()
        ):
            return None

        return document

    def run(self, documents: List[Any], **kwargs,) -> List[Any]:
        filtered_documents: List[Any] = []
        for document in documents:
            if self.process(document, **kwargs):
                filtered_documents.append(document)

        return self.component.run(filtered_documents, **kwargs,)
