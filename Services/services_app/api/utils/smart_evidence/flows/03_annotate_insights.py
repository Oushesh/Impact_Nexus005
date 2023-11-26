from pathlib import Path

import typer
from tqdm import tqdm
from app.models.annotation import AnnotatedInsight

from smart_evidence.components import Component
from smart_evidence.components.classifiers import *
from smart_evidence.components.extractors import *
from smart_evidence.flows.config_to_flow import get_flow
from smart_evidence.helpers.data_store import DataStore


def run_pipeline(
    index: str = "insights_dev",
    config_path: Path = Path("smart_evidence/flows/configs/annotate_insights.yaml"),
):
    flow = eval(get_flow(config_path))
    data_store = DataStore[AnnotatedInsight](index=index)

    for batch in tqdm(data_store.get_batches()):
        batch.sort(key=lambda x: len(x.text))
        batch = flow.run(batch)
        data_store.write_batch(batch)


if __name__ == "__main__":
    typer.run(run_pipeline)
