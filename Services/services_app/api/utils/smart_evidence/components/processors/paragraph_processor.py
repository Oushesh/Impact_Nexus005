"""Cleanup white-space and lines with 1-2 tokens."""
from enum import Enum
import re
from collections import defaultdict
from typing import Any, List
from app.models.documents import Document, DocumentType
from app.models.annotation import AnnotatedInsight
from app.models.impact_screening import Insight

from smart_evidence.components import BaseComponent
from smart_evidence.components.processors.base_processor import BaseProcessor
from smart_evidence.helpers.data import filter_dups, hash_document

SOURCE_TO_TEXT_FIELD = defaultdict(lambda: "text")
SOURCE_TO_TEXT_FIELD["core"] = "abstract"


class SplitterType(str, Enum):
    single_break = "single_break"
    double_break = "double_break"
    custom = "custom"
    fixed_strides = "fixed_strides"


class ParagraphProcessor(BaseProcessor):
    def __init__(self, component: BaseComponent, **data: Any):
        super().__init__(component, **data)
        self.paragraph_marker: SplitterType = self.component_config.get(
            "paragraph_marker", None
        )
        self.overlapping_strides: bool = self.component_config.get(
            "overlapping_strides", False
        )
        self.split_stride_length: int = self.component_config.get(
            "split_stride_length", 0
        )  # overlap length
        self.max_split_length: int = self.component_config.get(
            "max_split_length", 512
        )  # split length
        if self.paragraph_marker == SplitterType.custom:
            self.paragraph_split_pattern: str = self.component_config.get(
                "paragraph_split_pattern", ""
            )
            assert (
                len(self.paragraph_split_pattern) > 0
            ), "When selecting custom paragraph marker a regex pattern must be passed in as `paragraph_split_pattern`"

    def process(self, item: Document, **kwds) -> List[AnnotatedInsight]:  # type: ignore
        paragraphs = self.extract_processed_item(item)
        paragraphs = filter_dups(paragraphs)
        return [AnnotatedInsight(**paragraph.dict()) for paragraph in paragraphs]

    def run(self, documents: List[Document], **kwargs) -> List[AnnotatedInsight]:
        paragraph_documents = []
        for document in documents:
            paragraph_documents += self.process(document)
        return self.component.run(paragraph_documents, **kwargs)

    def split_new_lines(self, text, paragraph_boundary):
        # if '<div' in text:
        #     text = extract_text(text)
        paragraphs: List[str] = []
        if paragraph_boundary == SplitterType.single_break:
            paragraphs = re.split(r"\s*\n+\s*", text.strip())
        elif paragraph_boundary == SplitterType.double_break:
            paragraphs = re.split(r"\s*\n\n+\s*", text.strip())
        elif paragraph_boundary == SplitterType.custom:
            paragraphs = re.split(rf"{self.paragraph_split_pattern}", text.strip())
        elif paragraph_boundary == SplitterType.fixed_strides:
            paragraphs = self.add_overlapping_strides(texts=[text])
        return paragraphs

    def add_overlapping_strides(self, texts):
        """
        Adds overlapping texts between two consecutive paragraphs to supplement machine learning models with additional context.

        Args:
            texts List[str]: List of paragraphs split based on the paragraph boundary.

        Returns:
            List[str]: Paragraphs with overlapping strides.
        """
        start_idx = 0
        overlapping_pargraphs: List[str] = []
        for text in texts:
            text_length = len(text)
            while start_idx < text_length:
                if self.split_stride_length > 0 and start_idx > 0:
                    start_idx = (
                        self._valid_index(text, start_idx - self.split_stride_length)
                        + 1
                    )
                end_idx = self._valid_index(
                    text,
                    min(start_idx + self.max_split_length, text_length),
                )

                phrase = text[start_idx:end_idx]
                overlapping_pargraphs.append(phrase)
                start_idx = end_idx + 1
        return overlapping_pargraphs

    @staticmethod
    def _valid_index(document: str, idx: int) -> int:
        if idx <= 0:
            return 0
        if idx >= len(document):
            return len(document)
        new_idx = idx
        while new_idx > 0:
            if document[new_idx] in [" ", "\n", "\t"]:
                break
            new_idx -= 1
        return new_idx

    def annotate_hypothesis_curation(self, selectors, paragraph):
        meta = {}
        if selectors:
            hyp_annotations = [
                annotation
                for selector, annotation in selectors
                if (
                    re.sub(r"\s+", "", paragraph)
                    in re.sub(r"\s+", "", selector["exact"])
                )
                or (
                    re.sub(r"\s+", "", selector["exact"])
                    in re.sub(r"\s+", "", paragraph)
                )
            ]

            if hyp_annotations:
                meta = {"hypothesis_annotations": hyp_annotations}

        return meta

    def extract_quote_selectors_text(self, item: Document):
        if item.meta is None:
            return []
        selectors = [
            (anno["target"][0]["selector"], anno)
            for anno in item.meta.get("hypothesis_annotations", [])
            if "selector" in anno["target"][0]
        ]
        quote_selectors = [
            (
                next((s for s in selector if s["type"] == "TextQuoteSelector"), None),
                hyp_meta,
            )
            for selector, hyp_meta in selectors
        ]
        return quote_selectors

    def extract_processed_item(self, item: Document) -> List[Insight]:
        paragraph_candidates = []
        paragraph_boundary = None

        # choose paragraph splitter
        if not self.paragraph_marker and item.type == DocumentType.pdf:
            paragraph_boundary = SplitterType.double_break
        elif not self.paragraph_marker and item.type == DocumentType.html:
            paragraph_boundary = SplitterType.single_break
        else:
            paragraph_boundary = self.paragraph_marker

        # choose content field
        if item.abstract is not None and (
            item.abstract not in item.text or item.scraper == "core"
        ):
            paragraph_candidates += self.split_new_lines(
                item.abstract, paragraph_boundary
            )

        if item.scraper != "core":
            paragraph_candidates += self.split_new_lines(item.text, paragraph_boundary)

        selectors = self.extract_quote_selectors_text(item)

        def _insight_from_document(document, **overrides):
            attrs = document.dict(exclude_none=True)
            attrs.update(overrides)
            _document_id = attrs.pop("id")
            _id = hash_document(attrs, fields=["uri", "text"])
            return Insight(id=_id, document_id=_document_id, **attrs)

        processed_paragraphs = []
        for i, paragraph in enumerate(paragraph_candidates):
            only_words = re.sub(r"[\W\d_]+", " ", paragraph)
            word_tokens = re.split(r"\s+", only_words)
            if len(re.sub(r"[\s]+", "", only_words)) < 100 or len(word_tokens) < 20:
                continue

            insight = _insight_from_document(item, text=paragraph, par_index=i)
            if selectors:
                hypothesis_meta = self.annotate_hypothesis_curation(
                    selectors, paragraph
                )
                insight.meta.update(hypothesis_meta)
            else:
                insight.meta = None
            processed_paragraphs.append(insight)

        return processed_paragraphs
