"""
Created on Wed Oct  5 16:54:48 2022

@author: HP
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import spacy
import spacy_transformers  # noqa: F401
import torch
from sklearn.feature_extraction.text import CountVectorizer
from torch.nn import functional as F
from transformers import AutoModel, AutoTokenizer
from app.models.annotation import AnnotatedInsight, AnnotationType, InsightAnnotation

from smart_evidence.components import BaseComponent
from smart_evidence.components.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


def squash(value: torch.Tensor) -> torch.Tensor:
    if not torch.is_tensor(value):
        raise ValueError(
            f"Expected `torch.Tensor`, but got an unexpected `value` of type {value.__class__}"
        )
    if value.ndim == 2:
        return value
    return value.mean(dim=1)


def get_all_candidates(
    text: str, n_gram_range: Union[Tuple[int], List[int]]
) -> List[str]:
    count = CountVectorizer(ngram_range=n_gram_range, stop_words="english").fit([text])
    all_candidates = count.get_feature_names_out()
    return all_candidates


def torch_fast_mode() -> Callable:
    """use `torch.inference_mode()` if torch version is high enough"""
    try:
        return torch.inference_mode()
    except AttributeError:
        return torch.no_grad()


class ConceptExtractor:
    def __init__(self, **data: Any):
        spacy_model = data.get("spacy_model", "en_core_web_sm")
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            logger.exception(
                f"Can't find spaCy model {spacy_model}. Have you run `python -m spacy download {spacy_model}`?"
            )
        self.device = "cpu"
        self.top_k = data.get("top_k", 5)
        self.n_gram_range = data.get("n_gram_range", (1, 2))
        self.model = AutoModel.from_pretrained(
            data.get("bert_model", "sentence-transformers/all-MiniLM-L12-v2")
        ).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            data.get("bert_model", "sentence-transformers/all-MiniLM-L12-v2")
        )

    def get_candidates(self, text: str) -> List[str]:
        nouns = self.get_nouns(text)
        all_candidates = get_all_candidates(text, self.n_gram_range)
        candidates = list(filter(lambda candidate: candidate in nouns, all_candidates))
        return candidates

    def get_nouns(self, text: str) -> Set[str]:
        doc = self.nlp(text)
        nouns = set(token.text for token in doc if token.pos_ == "NOUN")
        noun_phrases = set(chunk.text.strip() for chunk in doc.noun_chunks)
        return nouns.union(noun_phrases)

    @torch_fast_mode()
    def get_embedding(self, source: Union[str, List[str]]):
        if isinstance(source, str):
            source = [source]
        tokens = self.tokenizer(
            source,
            padding=True,
            truncation=True,
            max_length=self.tokenizer.model_max_length,
            return_tensors="pt",
        ).to(self.device)
        outputs = self.model(**tokens, return_dict=True)
        embedding = self.parse_outputs(outputs)
        return embedding

    def parse_outputs(self, outputs: Dict[str, torch.Tensor]):
        value = None
        outputs_keys = outputs.keys()
        if len(outputs_keys) == 1:
            value = tuple(outputs.values())[0]
        else:
            for key in {"pooler_output", "last_hidden_state"}:
                if key in outputs_keys:
                    value = outputs[key]
                    break
        if value is None:
            raise RuntimeError(
                (
                    "No matching BERT keys found from model output. "
                    "Please make sure that the transformer model is BERT-based."
                )
            )
        return squash(value)

    def __call__(self, text: str) -> List[str]:
        candidates = self.get_candidates(text)
        if not candidates:
            return []
        text_embedding = self.get_embedding(text)
        candidate_embeddings = self.get_embedding(candidates)
        distances = F.cosine_similarity(
            text_embedding.unsqueeze(1), candidate_embeddings, dim=-1
        ).squeeze()
        if self.top_k > distances.numel():
            logger.warn(
                f"`top_k` has been adjusted because it is larger than the number of candidates."
            )
            top_k = distances.numel()
            _, indicies = torch.topk(distances, k=top_k)
        else:
            _, indicies = torch.topk(distances, k=self.top_k)

        if indicies.numel() == 1:
            return [candidates[indicies]]
        else:
            return [candidates[index] for index in indicies]
