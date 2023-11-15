from pathlib import Path
from typing import Dict, List
import typer
from datetime import datetime
from uuid import uuid4
import subprocess

from smart_evidence.components import Component
from smart_evidence.components.classifiers import (
    BoolQACompanyImpactClassifier,
    CompanyImpactClassifier,
    InsightClassifier,
)
from smart_evidence.components.data_stores import OpenSearchStore
from smart_evidence.flows.config_to_flow import get_flow, get_config

from app.models.annotation import AnnotatedInsight
from smart_evidence.data_models.document_store_schema import INSIGHTS_MAPPING


def evaluate_pipeline(
    config_path: Path = Path("smart_evidence/flows/configs/evaluation_config.yaml"),
):
    flow = eval(get_flow(config_path))
    flow_config = get_config(config_path)
    git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()

    # init evaluation boilerplate meta data
    evaluations: Dict = {
        "id": uuid4().hex,
        "flow_config": flow_config,
        "date": datetime.now(),
        "git_hash": git_hash,
    }

    print("Reminder: `batch_size` must always be equal to size of evaluation index")

    # run evaluation pipeline
    print(flow.evaluate(documents=[], evaluations=evaluations))
    print(f"Evaluation completed!")


if __name__ == "__main__":
    typer.run(evaluate_pipeline)
