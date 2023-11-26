from abc import abstractmethod
from typing import Any, Dict, List, Optional

from app.models.annotation import AnnotatedInsight
from app.models.documents import Document  # type: ignore
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.helpers import gpu_util


class BaseSummarizer(BaseComponent):
    def __init__(self, component: BaseComponent, **data: Any):
        """
        auto: choose gpu if present else use cpu
        cpu: use cpu
        cuda:{id} - cuda device id
        """
        super().__init__(component, **data)
        _device_id = self.component_config.get("device", "auto")
        self.content_field = self.component_config.get("content_field", "text")
        self.device: int = gpu_util.get_device_id(_device_id)
        self.model_name_or_path: str = self.component_config.get(
            "model_name_or_path", ""
        )
        self.evaluation_config: Dict = data.get("evaluation_config", {})
        self.config = data.get("config", {})

    @property
    def component(self) -> BaseComponent:
        """
        The Decorator delegates all work to the wrapped component.
        """

        return self._component

    def run(self, documents: List[Any], **kwds) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def process(self, document: Any, **kwds) -> Optional[Document]:
        raise NotImplementedError

    def evaluate(
        self, documents: List[Document], evaluations: Dict, **kwds
    ) -> Dict:
        raise NotImplementedError
