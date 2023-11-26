from tqdm import tqdm
from pathlib import Path
import typer
from app.models.documents import Document
from app.models.impact_screening import Insight

from smart_evidence.data_models.document_store_schema import (
    DOCUMENTS_MAPPING,
    INSIGHTS_MAPPING,
)
from smart_evidence.components.retrievers.sentence_transformer_retriever import (
    SentenceTransformerRetriever,
)

from smart_evidence.components.processors.paragraph_processor import ParagraphProcessor
from smart_evidence.components import Component
from smart_evidence.components.filters.insight_filter import InsightFilter
from smart_evidence.flows.config_to_flow import get_flow
from smart_evidence.helpers.data_store import DataStore

BATCH_SIZE = 10_000


def run(
    documents_index: str = "documents-new",
    insights_index: str = "insights-new",
    config_path: Path = Path("smart_evidence/flows/configs/extract_insights.yaml"),
):
    """Extract document elements, e.g. paragraphs, abstracts from documents.

    Args:
        input_folder (Path, optional): Defaults to Path("corpus/documents/").
        index (str, optional): Defaults to "haystack-paragraphs".
        skip_existing (bool, optional): Skip jsonl files that have any related document
            elements in elastic search. If False we still skip individual elements that have been
            uploaded but add new ones. Defaults to True.
    """
    ## define pipeline
    flow = eval(get_flow(config_path))

    # DocumentStore: holds all your data
    document_store = DataStore[Document](
        index=documents_index, document_class=Document, index_mapping=DOCUMENTS_MAPPING
    )

    insight_store = DataStore[Document](
        index=insights_index, document_class=Insight, index_mapping=INSIGHTS_MAPPING
    )
    n_insights = 0
    n_documents = 0
    for documents_batch in tqdm(document_store.get_batches()):
        n_documents += len(documents_batch)
        insights_batch = flow.run(documents_batch)
        n_insights += len(insights_batch)
        insight_store.write_batch(insights_batch)

    print(
        f"Uploaded {n_insights} insights to elasticsearch from {n_documents} documents."
    )


if __name__ == "__main__":
    typer.run(run)
