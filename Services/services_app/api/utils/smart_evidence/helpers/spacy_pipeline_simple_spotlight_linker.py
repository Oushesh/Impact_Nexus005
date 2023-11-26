import os
from pathlib import Path
from pyairtable import Table

import spacy
from smart_evidence.helpers import custom_functions

# from smart_evidence.helpers import concept_patterns
from smart_evidence.helpers import airtable_concept_patterns
from thinc.api import set_gpu_allocator, require_gpu

LANG = "en"

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]


nlp = spacy.blank(LANG)

concept_pattern_path = "assets/keywords_clean/patterns_airtable_impact.jsonl"
airtable_concept_patterns.create_concept_patterns(nlp, out_path=concept_pattern_path)

impact_concept_table = Table(AIRTABLE_API_KEY, "appGhfa7A73wMqhRB", "ImpactConcept")
formula = f"NOT(OR({{State}}='DISCARDED', {{State}}='DISABLED', {{State}}='GENERATED'))"
rows = impact_concept_table.all(view="Grid view", formula=formula)
impact_concepts = [
    {
        **ImpactConcept.from_airtable(**row).dict(),
        "type": "IMPACT",
    }
    for row in rows
]

nlp.add_pipe(
    "dbpedia_spotlight",
    config={
        "confidence": 0.35,
        "dbpedia_rest_endpoint": "http://172.17.0.1:2222/rest",
        "overwrite_ents": False,
    },
)

pipeline_path = Path("pipelines/en_ix_entity_ruler")
pipeline_path.mkdir(exist_ok=True, parents=True)
nlp.to_disk(pipeline_path)
