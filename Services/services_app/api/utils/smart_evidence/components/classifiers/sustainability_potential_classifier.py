from typing import Any, List, Optional

from spacy.language import Language
from spacy.tokens import Doc, Span
from transformers import pipeline

from app.models.annotation import AnnotatedInsight
from smart_evidence.components import BaseComponent
from smart_evidence.components.classifiers.base_classifier import BaseClassifier

CANDIDATE_LABELS = [
    "sustainability problem",
    "sustainability solution",
    "process description, fact or statement",
]

LABEL_TRANSLATOR = {
    "sustainability problem": "PROBLEM",
    "sustainability solution": "SOLUTION",
    "process description, fact or statement": "FACT",
}


class SustainabilityPotential(BaseClassifier):
    def __init__(self, component: BaseComponent, nlp: Language, **data: Any):
        super().__init__(component, **data)
        self.labels = list(LABEL_TRANSLATOR.values())
        self.classifier = pipeline(
            "zero-shot-classification", model="cross-encoder/nli-deberta-v3-large"
        )
        if not Span.has_extension("labels"):
            Span.set_extension("labels", default={})
        if not Doc.has_extension("labels"):
            Doc.set_extension("labels", default={})

    def predict(self, sentences):
        zeroshot_predictions = self.classifier(sentences, CANDIDATE_LABELS)
        if not isinstance(zeroshot_predictions, List):
            zeroshot_predictions = [zeroshot_predictions]

        return zeroshot_predictions

    def __call__(self, document: Doc, **kwargs: Any) -> Doc:
        sentences = list(document.sents)
        if Doc.has_extension("sentence_mask"):
            sentence_mask = document._.sentence_mask
        else:
            sentence_mask = [True] * len(sentences)

        masked_sentences = [
            sentence.text
            for sentence, mask in zip(document.sents, sentence_mask)
            if mask
        ]
        zs_predictions = self.predict(masked_sentences)

        sent_labels = set()
        for sentence, mask in zip(document.sents, sentence_mask):
            if mask:
                zs_label = LABEL_TRANSLATOR[zs_predictions.pop(0)["labels"][0]]
                sentence._.labels.update({"sustainability_potential": zs_label})
                sent_labels.add(zs_label)
            else:
                continue

        if "PROBLEM" in sent_labels and "SOLUTION" in sent_labels:
            doc_label = "PROBLEM+SOLUTION"
        elif "PROBLEM" in sent_labels:
            doc_label = "PROBLEM"
        elif "SOLUTION" in sent_labels:
            doc_label = "SOLUTION"
        else:
            doc_label = None

        if doc_label is not None:
            document._.labels.update({"sustainability_potential": doc_label})
        return document

    def process(self, document: Any, **kwds) -> Optional[AnnotatedInsight]:
        return self(document)

    def run(self, documents: List[Doc], **kwargs: Any) -> List[Doc]:
        documents = [self.process(document) for document in documents]
        return self.component.run(documents, **kwargs)
