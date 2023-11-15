from typing import Any, List, Optional

from spacy.language import Language
from spacy.tokens import Doc, Span
from transformers import BertForSequenceClassification, BertTokenizer, pipeline

from app.models.annotation import AnnotatedInsight
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.base_classifier import BaseClassifier

LABEL_TRANSLATOR = {
    "negative": "NEGATIVE",
    "positive": "POSITIVE",
    "neutral": "NEUTRAL",
}


class FinancialToneClassifier(BaseClassifier):
    def __init__(self, component: BaseComponent, nlp: Language, **data: Any):
        super().__init__(component, **data)
        self.labels = list(LABEL_TRANSLATOR.values())
        self.finbert = pipeline(
            "sentiment-analysis",
            model=BertForSequenceClassification.from_pretrained(
                "yiyanghkust/finbert-tone", num_labels=3
            ),
            tokenizer=BertTokenizer.from_pretrained("yiyanghkust/finbert-tone"),
        )
        if not Span.has_extension("labels"):
            Span.set_extension("labels", default={})
        if not Doc.has_extension("labels"):
            Doc.set_extension("labels", default={})

    def __call__(self, document: Doc, **kwargs: Any) -> Doc:
        sentences = list(document.sents)
        if Doc.has_extension("sentence_mask"):
            sentence_mask = document._.sentence_mask
        else:
            sentence_mask = [True] * len(sentences)
        masked_sentences = [
            sentence.text for sentence, mask in zip(sentences, sentence_mask) if mask
        ]
        predictions = self.finbert(masked_sentences)

        sent_labels = set()
        for sentence, mask in zip(document.sents, sentence_mask):
            if mask:
                label = LABEL_TRANSLATOR[predictions.pop(0)["label"]]
                sentence._.labels.update({"financial_tone": label})
                sent_labels.add(label)
            else:
                continue

        if "POSITIVE" in sent_labels and "NEGATIVE" in sent_labels:
            doc_label = "POSITIVE_NEGATIVE"
        elif "NEGATIVE" in sent_labels:
            doc_label = "NEGATIVE"
        elif "POSITIVE" in sent_labels:
            doc_label = "POSITIVE"
        elif "NEUTRAL" in sent_labels:
            doc_label = "NEUTRAL"
        else:
            doc_label = None

        if doc_label is not None:
            document._.labels.update({"financial_tone": doc_label})
        return document

    def process(self, document: Any, **kwds) -> Optional[AnnotatedInsight]:
        return self(document)

    def run(self, documents: List[Doc], **kwargs: Any) -> List[Doc]:
        documents = [self.process(document) for document in documents]
        return self.component.run(documents, **kwargs)
