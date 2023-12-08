from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema

from services_app.api.routers.build_knowledgebase import router as build_knowledgebase_router
from services_app.api.routers.parquet_conversion import router as parquet_conversion_router
from services_app.api.routers.model_downloader import router as model_downloader_router
from services_app.api.routers.data_processor_classification_job import router as data_processor_classification_job_router
from services_app.api.routers.incoming_data_deepcheck import router as incoming_data_deepcheck_router
from services_app.api.routers.haystack_crawler import router as haystack_crawler_router

#Call the routers from ninja
api = NinjaAPI()

api.add_router("/",build_knowledgebase_router)
api.add_router("/",parquet_conversion_router)
api.add_router("/downloader",model_downloader_router)
api.add_router("/jobs",data_processor_classification_job_router)
api.add_router("/deepcheck",incoming_data_deepcheck_router)
api.add_router("/crawler",haystack_crawler_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/",api.urls),
]
