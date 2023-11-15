import os

os.chdir("../..")

from argparse import ArgumentError
from glob import glob
from pathlib import Path
from typing import Counter

import spacy
import srsly
import typer
from spacy.tokens import Doc
from tqdm import tqdm

from scripts.components import (
    component_lowercase_lemmas,
    entity_ruler,
    financial_tone_classifier,
    keyword_ruler,
    predict_domain_from_keywords,
    sentence_masker,
    sustainability_potential_classifier,
)
from scripts.data_helpers import (
    extract_sentence_entities,
    filter_dups,
    filter_item_fields,
    hash_documents,
)
from scripts.extract_paragraphs import paragraph_generator
