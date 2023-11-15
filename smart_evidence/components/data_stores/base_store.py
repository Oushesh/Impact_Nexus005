from abc import abstractmethod
from typing import Any, Dict, List

from smart_evidence.components.base_component import BaseComponent
from smart_evidence.data_models.document_store_schema import *
from smart_evidence.helpers.errors import DocumentStoreError

BASE_QUERY: Any = {"query": {"match_all": {}}}
HUMAN_QUERY = {
    "query": {
        "nested": {
            "path": "annotations",
            "query": {"term": {"annotations.type": "HUMAN"}},
        }
    }
}
SIMILARITY_SPACE_TYPE_MAPPINGS = {
    "nmslib": {"cosine": "cosinesimil", "dot_product": "innerproduct", "l2": "l2"},
    "faiss": {"cosine": "innerproduct", "dot_product": "innerproduct", "l2": "l2"},
}


class BaseStore(BaseComponent):
    def __init__(self, component: BaseComponent, **data):
        super().__init__(component, **data)
        self.mode = self.component_config.get("mode", "read")
        self.batch_size = self.component_config.get("batch_size", 10)
        if self.mode == "read":
            self.batches = self.get_batches(**self.component_config)
        elif self.mode == "write":
            self.exclude_fields = self.component_config.get("exclude_fields", [])

    @property
    def component(self) -> BaseComponent:
        """
        The Decorator delegates all work to the wrapped component.
        """

        return self._component

    def run(self, documents: List[Any], **kwds,) -> List[Any]:
        if self.mode == "write":
            self.write_batch(documents)
            return self.component.run(documents, **kwds)
        elif self.mode == "read":
            return self.component.run(next(self.batches), **kwds)

        raise DocumentStoreError

    def get_batches(self, **kwds):
        def _item_batcher(items):
            batch = []
            for item in items:
                batch.append(item)
                if len(batch) == self.batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

        for batch in _item_batcher(self.item_generator(**kwds)):
            yield batch

    def process(self, document: Any, **kwds) -> Any:
        raise NotImplementedError

    @abstractmethod
    def item_generator(self, **kwds):
        raise NotImplementedError

    @abstractmethod
    def write_batch(self, batch: List[Any]):
        raise NotImplementedError

    def evaluate(self, documents: List[Any], evaluations: Dict, **kwds) -> Any:
        if self.mode == "write":
            self.write_batch([evaluations])
            return self.component.evaluate(documents, evaluations, **kwds)
        elif self.mode == "read":
            return self.component.evaluate(next(self.batches), evaluations, **kwds)
