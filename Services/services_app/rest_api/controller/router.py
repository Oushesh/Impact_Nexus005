from fastapi import APIRouter
from Services.services_app.rest_api.controller import base
from Services.services_app.rest_api.controller import eu_taxonomy_classification

router = APIRouter()

router.include_router(base.router, tags=["Base"])
router.include_router(
    eu_taxonomy_classification.router, tags=["EU Taxonomy Classification"]
)
