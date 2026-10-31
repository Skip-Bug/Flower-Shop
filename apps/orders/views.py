from decimal import Decimal

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.models import Bouquet, Event

from .forms import ConsultationRequestForm, OrderForm
from .models import Order
from .services import pick_bouquet_for_quiz


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
    occasion_slug = request.session.get("event")
    budget_key = request.session.get("budget")
    bouquet = pick_bouquet_for_quiz(occasion_slug, budget_key)
    return render(request, "result.html", {"bouquet": bouquet})


def order(request, slug):
    bouquet = get_object_or_404(Bouquet, slug=slug, is_active=True)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.bouquet = bouquet
            new_order.bouquet_snapshot = {
                "id": bouquet.id,
                "title": bouquet.title,
                "slug": bouquet.slug,
                "price": str(bouquet.price),
                "description": bouquet.description,
                "composition": bouquet.composition,
                "size": bouquet.size,
            }
            new_order.bouquet_price = bouquet.price
            new_order.delivery_fee = Decimal("0")
            new_order.total_price = bouquet.price + new_order.delivery_fee
            new_order.save()
            request.session["last_order_id"] = new_order.id
            return redirect("orders:order_done", order_id=new_order.pk)
    else:
        form = OrderForm()

    return render(request, "order.html", {"form": form, "bouquet": bouquet})


def order_done(request, order_id):
    if request.session.get("last_order_id") != order_id:
        raise Http404("Заказ не найден")

    order = get_object_or_404(Order, pk=order_id)
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
