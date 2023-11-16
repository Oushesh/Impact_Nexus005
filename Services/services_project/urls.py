from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Schema
from services_app.api.routers.build_knowledgebase import router as build_knowledgebase_router
from services_app.api.routers.data_optimisation import router as data_optimisation_router

#Call the routers from ninja
api = NinjaAPI()
api.add_router("/",build_knowledgebase_router)
api.add_router("/",data_optimisation_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/",api.urls),
]
