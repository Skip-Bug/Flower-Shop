from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("quiz/", views.quiz, name="quiz"),
    path("quiz/step/", views.quiz_step, name="quiz_step"),
    path("result/", views.result, name="result"),
    path("order/", views.order, name="order"),
    path("order/step/", views.order_step, name="order_step"),
]
