from app.models.documents import Document
from smart_evidence.components.base_component import BaseComponent
from smart_evidence.components.retrievers.base_retriever import BaseRetriever
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Any, Union, List


class SentenceTransformerRetriever(BaseRetriever):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.embedding_model = SentenceTransformer(self.model_name_or_path)

    def __call__(self, texts: Union[List[str], str]) -> np.ndarray:
        # texts can be a list of strings
        # get back list of numpy embedding vectors
        emb: np.ndarray = self.embedding_model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=self.show_progress_bar,
            convert_to_numpy=True,
        )  # type: ignore
        return emb

    def process(self, document: Any, **kwds) -> Any:
        content = getattr(document, self.content_field)
        document.embedding = self(content)  # type: ignore
        return document

    def run(self, documents: List[Any], **kwds) -> List[Any]:
        for idx, embedding in enumerate(
            self([getattr(document, self.content_field) for document in documents])
        ):
            documents[idx].embedding = embedding

        return self.component.run(documents, **kwds)
