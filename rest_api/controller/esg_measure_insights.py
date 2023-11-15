import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseConfig

from app.models.documents import Document
from app.models.impact_screening import Insight
from rest_api.config import (
    CONCURRENT_REQUEST_PER_WORKER,
    LOG_LEVEL,
)
from rest_api.controller.errors.http_error import http_error_handler
from rest_api.controller.utils import RequestLimiter
from rest_api.schema import (
    InsightForConcept,
    InsightsForConceptRequest,
    InsightsForConceptResponse,
)
from smart_evidence.components import Component
from smart_evidence.components.classifiers.concept_insight_relatedness_classifier import (
    ESGRelatedInsightsClassifier,
)
from smart_evidence.components.retrievers.sentence_transformer_retriever import (
    SentenceTransformerRetriever,
)
from smart_evidence.data_models.document_store_schema import INSIGHTS_MAPPING
from smart_evidence.components.data_stores import OpenSearchStore

logging.getLogger("haystack").setLevel(LOG_LEVEL)
logger = logging.getLogger("haystack")


BaseConfig.arbitrary_types_allowed = True

router = APIRouter()

## instantiate pipeline components

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)
logging.info("Concurrent requests per worker: {CONCURRENT_REQUEST_PER_WORKER}")


@router.post(
    "/esg_measure_insights",
    response_model=InsightsForConceptResponse,
    response_model_exclude_none=True,
)
def retriever_concept_related_insights(request: InsightsForConceptRequest):
    """
    This endpoint receives the insight paragraphs related to the input company concept.
    """
    with concurrency_limiter.run():
        if not request.concept.strip():
            return http_error_handler(
                request,  # type: ignore
                exc=HTTPException(
                    status_code=400, detail="Company concept should not be empty"
                ),
            )
        response = None
        return response
