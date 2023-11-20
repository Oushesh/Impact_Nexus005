from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema
from services_app.api.routers.build_knowledgebase import router as build_knowledgebase_router
from services_app.api.routers.parquet_conversion import router as parquet_conversion_router
from services_app.api.routers.model_downloader import router as model_downloader_router

#Call the routers from ninja
api = NinjaAPI()
api.add_router("/",build_knowledgebase_router)
api.add_router("/",parquet_conversion_router)
api.add_router("/downloader",model_downloader_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/",api.urls),
]
