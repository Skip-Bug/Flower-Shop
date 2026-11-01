from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from requests.exceptions import RequestException
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError, NotFoundError

from apps.catalog.models import Bouquet, Event, Store

from .forms import ConsultationRequestForm, OrderForm
from .models import Order
from .services import (
    build_order_from_form,
    create_yookassa_payment,
    pick_bouquet_for_quiz,
    place_order,
)


@require_http_methods(["GET", "POST"])
def quiz(request):
    if request.method == "POST":
        request.session["event"] = request.POST.get("event")
        return redirect("orders:quiz_step")

    events = Event.objects.filter(is_active=True)
    return render(request, "quiz.html", {"events": events})


@require_http_methods(["GET", "POST"])
def quiz_step(request):
    if request.method == "POST":
        request.session["budget"] = request.POST.get("budget")
        return redirect("orders:result")

    return render(request, "quiz-step.html")


@require_GET
def result(request):
    occasion_slug = request.session.pop("event", None)
    budget_key = request.session.pop("budget", None)
    bouquet = pick_bouquet_for_quiz(occasion_slug, budget_key)
    stores = Store.objects.filter(is_active=True)
    return render(request, "result.html", {"bouquet": bouquet, "stores": stores})


@require_http_methods(["GET", "POST"])
def order(request, slug):
    bouquet = get_object_or_404(Bouquet, slug=slug, is_active=True)

    if request.method == "GET":
        form = OrderForm()
        return render(request, "order.html", {"form": form, "bouquet": bouquet})

    form = OrderForm(request.POST)
    if not form.is_valid():
        return render(request, "order.html", {"form": form, "bouquet": bouquet})

    new_order = build_order_from_form(form, bouquet)

    if not place_order(form, new_order):
        return render(request, "order.html", {"form": form, "bouquet": bouquet})

    if new_order.payment_method == "online":
        try:
            payment = create_yookassa_payment(new_order, request)
        except (ApiError, RequestException):
            form.add_error(
                None,
                "Не удалось создать платёж. Попробуйте ещё раз через минуту — "
                "если ошибка повторится, свяжитесь с нами по телефону.",
            )
            return render(request, "order.html", {"form": form, "bouquet": bouquet})

        new_order.payment_id = payment.id
        new_order.save(update_fields=["payment_id"])
        request.session["last_order_id"] = new_order.id
        return redirect(payment.confirmation.confirmation_url)

    request.session["last_order_id"] = new_order.id
    return redirect("orders:order_done", order_id=new_order.pk)


@require_GET
def order_done(request, order_id):
    if str(request.session.get("last_order_id")) != str(order_id):
        raise Http404("Заказ не найден")

    order = get_object_or_404(Order, pk=order_id)
    request.session.pop("last_order_id", None)
    return render(request, "order_done.html", {"order": order})


@require_GET
def consultation(request):
    form = ConsultationRequestForm()
    return render(request, "consultation.html", {"form": form})


@require_POST
def consultation_send(request):
    form = ConsultationRequestForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("orders:consultation_done")

    return render(request, "consultation.html", {"form": form})


@require_GET
def consultation_done(request):
    return render(request, "consultation_done.html")


@require_GET
def payment_success(request, order_id):
    """Поодтвердение оплаты"""
    if str(request.session.get("last_order_id")) != str(order_id):
        raise Http404("Заказ не найден")

    order = get_object_or_404(Order, pk=order_id)
    request.session.pop("last_order_id", None)

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    try:
        payment = Payment.find_one(order.payment_id)
    except (NotFoundError, ApiError):
        return render(request, "order_done.html", {"order": order})
    if payment.status == "succeeded":
        order.status = "paid"
        order.paid_at = timezone.now()
    elif payment.status == "canceled":
        order.status = "canceled"
    order.save()
    return render(request, "order_done.html", {"order": order})


@staff_member_required
@require_GET
def florist_dashboard(request):
    """Показывает список заказов для флористов"""
    active_statuses = [
        "pending_cash",
        "paid",
    ]

    orders = Order.objects.filter(status__in=active_statuses).order_by("created_at")

    return render(request, "florist_dashboard.html", {"orders": orders})
