import os
from pathlib import Path


EU_TAXONOMY_CLASSIFICATION_CONFIG_PATH = Path(
    os.getenv(
        "EU_TAXONOMY_CLASSIFICATION_CONFIG_PATH",
        str(
            (
                Path(__file__).parent / "pipeline" / "eu_taxonomy_classification.yaml"
            ).absolute()
        ),
    )
)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ROOT_PATH = os.getenv("ROOT_PATH", "/")

CONCURRENT_REQUEST_PER_WORKER = int(os.getenv("CONCURRENT_REQUEST_PER_WORKER", "4"))
