from django.shortcuts import redirect, render

from apps.catalog.models import Event


def quiz(request):
    if request.method == "POST":
        request.session["event"] = request.POST.get("event")
        return redirect("orders:quiz_step")

    events = Event.objects.filter(is_active=True)
    return render(request, "quiz.html", {"events": events})


def quiz_step(request):
    return render(request, "quiz-step.html")


def result(request):
    return render(request, "result.html")


def order(request):
    return render(request, "order.html")


def order_step(request):
    return render(request, "order-step.html")
