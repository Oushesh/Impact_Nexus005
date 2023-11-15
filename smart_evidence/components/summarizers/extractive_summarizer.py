import logging
from typing import Any, Dict, List, Optional
from tqdm import tqdm
from app.models.annotation import AnnotatedInsight
from app.models.documents import Document
from smart_evidence.components import BaseComponent
from smart_evidence.components.summarizers import BaseSummarizer
from transformers.pipelines import pipeline, SummarizationPipeline


logger = logging.getLogger(__name__)


class ExtractiveSummarizer(BaseSummarizer):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)

        self.pipeline = pipeline(
            task="summarization",
            model=self.model_name_or_path,
            pipeline_class=SummarizationPipeline,
            device=self.device,
        )
        self.summary_field = self.component_config.get("summary_field", "summary")
        self.summary_min_length = self.component_config.get("summary_min_length", 20)
        self.summary_max_length = self.component_config.get("summary_max_length", 50)

    def process(self, document: Document, **kwds) -> Document:
        content = getattr(document, self.content_field)
        if not len(content) or len(content) < self.summary_min_length:
            return document
        summary = self.pipeline(
            content,
            min_length=self.summary_min_length,
            max_length=self.summary_max_length,
        )[0].get("summary_text")
        setattr(document, self.summary_field, summary)
        return document

    def run(
        self,
        documents: List[Any],
        **kwds,
    ) -> List[Any]:

        processed_documents = []
        for document in tqdm(documents):
            processed_document = self.process(document)
            if processed_document is not None:
                processed_documents.append(processed_document)

        return self.component.run(processed_documents, **kwds)
