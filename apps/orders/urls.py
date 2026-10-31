from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("quiz/", views.quiz, name="quiz"),
    path("quiz/step/", views.quiz_step, name="quiz_step"),
    path("result/", views.result, name="result"),
    path("order/<slug:slug>/", views.order, name="order"),
    path("order/<int:order_id>/done/", views.order_done, name="order_done"),
    path("consultation/", views.consultation, name="consultation"),
    path("consultation/send/", views.consultation_send, name="consultation_send"),
    path("consultation/done/", views.consultation_done, name="consultation_done"),
    path(
        "order/<int:order_id>/payment-success/",
        views.payment_success,
        name="payment_success",
    ),
]
