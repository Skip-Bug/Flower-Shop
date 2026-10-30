from django.shortcuts import redirect, render

from apps.catalog.models import Event

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


def order(request):
    return render(request, "order.html")


def order_step(request):
    return render(request, "order-step.html")
