from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("catalog/", views.catalog, name="catalog"),
    path("card/", views.card, name="card"),
    path("consultation/", views.consultation, name="consultation"),
]
