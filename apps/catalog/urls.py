from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("catalog/", views.catalog, name="catalog"),
    path("bouquet/<slug:slug>/", views.bouquet_detail, name="bouquet_detail"),
]
