from abc import abstractmethod
from typing import Any, List, Optional, Dict

from tqdm import tqdm

from app.models.annotation import AnnotatedInsight
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.helpers import gpu_util


class BaseExtractor(BaseComponent):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.content_field: str = self.component_config.get("content_field", "text")
        _device_id = self.component_config.get("device", "auto")
        self.device: int = gpu_util.get_device_id(_device_id)

    @property
    def component(self) -> BaseComponent:
        """
        The Decorator delegates all work to the wrapped component.
        """

        return self._component

    def run(self, documents: List[Any], **kwds) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def process(self, document: Any, **kwds) -> Optional[AnnotatedInsight]:
        raise NotImplementedError
