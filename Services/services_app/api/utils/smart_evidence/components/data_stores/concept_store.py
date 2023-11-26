from typing import Any

from app.models.concepts import ConceptML
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.data_stores.base_store import BaseStore
from smart_evidence.helpers.concept_stores import (  # ruff: disable: F401
    get_concepts,
)


class ConceptStore(BaseStore):
    def __init__(self, component: BaseComponent, **data):
        super().__init__(component=component, **data)
        if self.mode == "write":
            raise NotImplementedError
        elif self.mode == "read":
            self.concept_retriever = eval(
                self.component_config.get("concept_retriever", "")
            )
            self.query = self.component_config.get("query", {})
            self.document_class = eval(self.component_config.get("document_class", ""))

    def write_batch(self, batch: Any, **kwds):
        raise NotImplementedError

    def _from_hit(self, hit):
        document = self.document_class(**hit)
        return document

    def item_generator(self, **kwds):
        hits = self.concept_retriever(self.query)
        document_generator = (self._from_hit(hit) for hit in hits)
        return document_generator
