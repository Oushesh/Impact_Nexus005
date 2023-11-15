from pathlib import Path
import dotenv

dotenv.load_dotenv()
import typer

from smart_evidence.components import *  # pylint: disable=W0401,W0614
from smart_evidence.components.data_stores import *  # pylint: disable=W0401,W0614
from smart_evidence.components.classifiers import *  # pylint: disable=W0401,W0614
from smart_evidence.components.extractors import *  # pylint: disable=W0401,W0614
from smart_evidence.components.filters import *  # pylint: disable=W0401,W0614
from smart_evidence.components.processors import *  # pylint: disable=W0401,W0614
from smart_evidence.components.retrievers import *  # pylint: disable=W0401,W0614
from smart_evidence.flows.config_to_flow import get_flow


def run_pipeline(
    config_path: Path = Path("smart_evidence/flows/configs/index_documents.yaml"),
):
    flow = eval(get_flow(config_path))  # pylint: disable=W0123
    count = 0
    try:
        result = flow.run(documents=[])
        while len(result):
            count += len(result)
            # same as before
            result = flow.run(documents=[])
            print(f"Pipeline has processed {count} docs.")
    except StopIteration:
        print(f"Pipeline excecution has finished after processing {count} docs.")


if __name__ == "__main__":
    typer.run(run_pipeline)
