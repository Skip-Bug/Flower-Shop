from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from yookassa import Configuration, Payment

from apps.catalog.models import Bouquet, Event

from .forms import ConsultationRequestForm, OrderForm
from .models import Order
from .services import (
    build_order_from_form,
    create_yookassa_payment,
    pick_bouquet_for_quiz,
)


def quiz(request):
    if request.method == "POST":
        request.session["event"] = request.POST.get("event")
        return redirect("orders:quiz_step")

    events = Event.objects.filter(is_active=True)
    return render(request, "quiz.html", {"events": events})


def quiz_step(request):
    if request.method == "POST":
        request.session["budget"] = request.POST.get("budget")
        return redirect("orders:result")

    return render(request, "quiz-step.html")


def result(request):
    occasion_slug = request.session.pop("event", None)
    budget_key = request.session.pop("budget", None)
    bouquet = pick_bouquet_for_quiz(occasion_slug, budget_key)
    return render(request, "result.html", {"bouquet": bouquet})


def order(request, slug):
    bouquet = get_object_or_404(Bouquet, slug=slug, is_active=True)

    if request.method == "GET":
        form = OrderForm()
        return render(request, "order.html", {"form": form, "bouquet": bouquet})

    form = OrderForm(request.POST)
    if not form.is_valid():
        return render(request, "order.html", {"form": form, "bouquet": bouquet})

    new_order = build_order_from_form(form, bouquet)

    if new_order.payment_method == "online":
        new_order.save()
        request.session["last_order_id"] = new_order.id
        payment = create_yookassa_payment(new_order, request)
        new_order.payment_id = payment.id
        new_order.save(update_fields=["payment_id"])
        return redirect(payment.confirmation.confirmation_url)

    new_order.status = "pending_cash"
    new_order.save()
    request.session["last_order_id"] = new_order.id
    return redirect("orders:order_done", order_id=new_order.pk)


def order_done(request, order_id):
    if str(request.session.get("last_order_id")) != str(order_id):
        raise Http404("Заказ не найден")

    order = get_object_or_404(Order, pk=order_id)
    request.session.pop("last_order_id", None)
    return render(request, "order_done.html", {"order": order})


def consultation(request):
    form = ConsultationRequestForm()
    return render(request, "consultation.html", {"form": form})


def consultation_send(request):
    if request.method != "POST":
        return redirect("orders:consultation")

    form = ConsultationRequestForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("orders:consultation_done")

    return render(request, "consultation.html", {"form": form})


def consultation_done(request):
    return render(request, "consultation_done.html")


def payment_success(request, order_id):
    """Поодтвердение оплаты"""
    if str(request.session.get("last_order_id")) != str(order_id):
        raise Http404("Заказ не найден")

    order = get_object_or_404(Order, pk=order_id)
    request.session.pop("last_order_id", None)

    # TO DO: В MVP мы просто меняем статус, если заказ новый.
    # В проде здесь ОБЯЗАТЕЛЬНО нужно делать запрос к API ЮKassa (Payment.find_one)
    # чтобы убедиться, что деньги реально пришли, а не просто человек вернулся по ссылке.
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    payment = Payment.find_one(order.payment_id)
    if payment.status == "succeeded":
        order.status = "paid"
        order.paid_at = timezone.now()
    elif payment.status == "canceled":
        order.status = "canceled"
    order.save()
    return render(request, "order_done.html", {"order": order})
