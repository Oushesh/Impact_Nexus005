from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema
from services_app.api.routers.build_knowledgebase import router as build_knowledgebase_router

#Call the routers from ninja
api = NinjaAPI()
api.add_router("/",build_knowledgebase_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/",api.urls),
]
