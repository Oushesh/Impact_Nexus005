import logging
from typing import List, Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseConfig
from app.models.annotation import AnnotatedInsight
from app.models.documents import Document
from app.models.impact_screening import Insight
from rest_api.config import (
    CONCURRENT_REQUEST_PER_WORKER,
    EU_TAXONOMY_CLASSIFICATION_CONFIG_PATH,
    LOG_LEVEL,
)
from rest_api.controller.errors.http_error import http_error_handler
from rest_api.controller.utils import RequestLimiter
from rest_api.schema import (
    EUTaxonomyClassificationRequest,
    EUTaxonomyClassificationResponse,
)
from smart_evidence.components import Component
from smart_evidence.components.classifiers import (
    EUTaxonomyClassifier,
    InsightClassifier,
    ESGRelatedConceptsClassifier,
)
from smart_evidence.components.data_stores import (
    OpenSearchStore,
)
from smart_evidence.components.retrievers import SentenceTransformerRetriever
from smart_evidence.components.processors import ExtractScraperHTML, ParagraphProcessor
from smart_evidence.flows.config_to_flow import get_flow

logging.getLogger("smart-evidence").setLevel(LOG_LEVEL)
logger = logging.getLogger("smart-evidence")


BaseConfig.arbitrary_types_allowed = True

router = APIRouter()

## instantiate pipeline components
flow = eval(get_flow(EU_TAXONOMY_CLASSIFICATION_CONFIG_PATH))  # pylint: disable=W0123

concurrency_limiter = RequestLimiter(CONCURRENT_REQUEST_PER_WORKER)
logging.info(f"Concurrent requests per worker: {CONCURRENT_REQUEST_PER_WORKER}")


@router.post(
    "/eu_taxonomy_classification",
    response_model=List[EUTaxonomyClassificationResponse],
    response_model_exclude_none=True,
)
def classify_eu_taxonomy_activities(request: EUTaxonomyClassificationRequest):
    """
    This endpoint receives the company concepts based on eu taxonomy activities that are
    related to the input text insight.
    """
    with concurrency_limiter.run():
        if not request.urls:
            return http_error_handler(
                request,  # type: ignore
                exc=HTTPException(
                    status_code=400, detail="Document URL(s) should not be empty"
                ),
            )
        response: List[EUTaxonomyClassificationResponse] = []
        try:
            result: List[AnnotatedInsight] = flow.run(documents=request)
            for document in result:
                activities = []
                if document.get_last_machine_annotations():
                    activities = (
                        document.get_last_machine_annotations().tasks.concepts.company_concepts
                    )
                response.append(
                    EUTaxonomyClassificationResponse(
                        **document.dict(exclude={"embedding"}),
                        activities=activities,  # type: ignore
                    )
                )
        except Exception as e:
            # TODO: have consistent logger message patterns
            logger.error(msg=f"{e}")
        return response
