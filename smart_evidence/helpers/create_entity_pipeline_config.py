from pathlib import Path

import spacy
from smart_evidence.helpers import custom_functions

# from smart_evidence.helpers import concept_patterns
from smart_evidence.helpers import airtable_concept_patterns
from thinc.api import set_gpu_allocator, require_gpu

set_gpu_allocator("pytorch")
require_gpu(0)

MODEL_NAME = "en_core_web_trf"

nlp = spacy.load(MODEL_NAME)

concept_pattern_path = "assets/keywords_clean/patterns_airtable.jsonl"
airtable_concept_patterns.create_concept_patterns(nlp, out_path=concept_pattern_path)

base_components = nlp.component_names
nlp.add_pipe("lower_case_lemmas", after="lemmatizer")
nlp.add_pipe("ix_entity_ruler", after="ner")
nlp.add_pipe("reference_value_expansion", after="ix_entity_ruler")
nlp.add_pipe("ix_entity_ruler_filter", after="reference_value_expansion")
ruler = nlp.add_pipe(
    "entity_ruler", config=dict(overwrite_ents=True), after="ix_entity_ruler_filter"
)
ruler.from_disk(concept_pattern_path)

pipeline_path = Path("pipelines/en_ix_entity_ruler")
pipeline_path.mkdir(exist_ok=True, parents=True)
nlp.to_disk(pipeline_path)
