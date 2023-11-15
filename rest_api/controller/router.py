from fastapi import APIRouter
from rest_api.controller import base, eu_taxonomy_classification


router = APIRouter()

router.include_router(base.router, tags=["Base"])
router.include_router(
    eu_taxonomy_classification.router, tags=["EU Taxonomy Classification"]
)
