from typing import Dict, List, Optional, Union

from pydantic import BaseConfig, BaseModel, Extra
from app.models.annotation import SimpleConcept
from app.models.impact_screening import Insight

BaseConfig.arbitrary_types_allowed = True


class InsightsForConceptRequest(BaseModel):
    concept: str
    filters: Optional[Dict[str, Union[Dict, List, str, int, float, bool]]] = None
    top_k: int = 10

    class Config:
        # Forbid any extra fields in the request to avoid silent failures
        extra = Extra.forbid


class InsightForConcept(BaseModel):
    concept: str = ""
    text: str = ""
    document_id: str
    title: Optional[str] = None
    scraper: str
    url: Optional[str]
    similarity_score: float
    confidence_score: float = 0.0


class InsightsForConceptResponse(BaseModel):
    concept: str = ""
    results: List[InsightForConcept] = []


class EUTaxonomyClassificationRequest(BaseModel):
    venture_id: str = ""
    urls: List[str] = []

    class Config:
        # Forbid any extra fields in the request to avoid silent failures
        extra = Extra.forbid


class EUTaxonomyClassificationResponse(Insight):
    activities: Optional[List[SimpleConcept]] = []
