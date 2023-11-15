from abc import abstractmethod
from typing import Any, List, Dict


class BaseComponent:
    """
    The base Component interface defines operations that can be altered by decorators.
    """

    def __init__(self, component: "BaseComponent", **data: Any):
        self._component = component
        self.config = data.get("config", {})
        self.component_config = data.get("component_config", {})

    @abstractmethod
    def process(self, document: Any, **kwds) -> Any:
        return document

    @abstractmethod
    def run(self, documents: List[Any], **kwds) -> List[Any]:
        pass

    @abstractmethod
    def evaluate(self, documents: List[Any], evaluations: Dict, **kwds) -> Any:
        pass


class Component(BaseComponent):
    """
    Concrete Components provide default implementations of the operations. There
    might be several variations of these classes.
    """

    def __init__(self, **data: Any):
        pass

    def process(self, document: Any, **kwds) -> Any:
        return document

    def run(self, documents: List[Any], **kwds) -> List[Any]:
        return documents

    def evaluate(self, documents: List[Any], evaluations: Dict, **kwds) -> Dict:
        return evaluations
