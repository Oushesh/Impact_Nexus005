from abc import abstractmethod

from tqdm import tqdm
import numpy as np
from typing import Any, Optional, Union, List
from torch import Tensor

from app.models.annotation import AnnotatedInsight
from app.models.documents import Document
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.helpers import gpu_util


class BaseRetriever(BaseComponent):
    def __init__(self, component: BaseComponent, **data: Any):
        """
        auto: choose gpu if present else use cpu
        cpu: use cpu
        cuda:{id} - cuda device id
        """
        super().__init__(component, **data)
        _device_id = self.component_config.get("device", "auto")
        self.device: int = gpu_util.get_device_id(_device_id)
        self.model_name_or_path: str = self.component_config.get(
            "model_name_or_path", ""
        )
        self.batch_size = self.component_config.get("batch_size", 8)
        self.content_field = self.component_config.get("content_field", "text")
        self.show_progress_bar = self.component_config.get("show_progress_bar", False)

    @property
    def component(self) -> BaseComponent:
        """
        The Decorator delegates all work to the wrapped component.
        """

        return self._component

    def run(self, documents: List[Any], **kwds) -> List[Any]:
        raise NotImplementedError

    @abstractmethod
    def process(self, document: Any, **kwds) -> Any:
        raise NotImplementedError
