from django.shortcuts import render

from .models import Bouquet


def index(request):
    recommended_bouquets = Bouquet.objects.filter(is_active=True).order_by("?")[:3]
    return render(
        request,
        "index.html",
        {"recommended_bouquets": recommended_bouquets},
    )


def catalog(request):
    bouquets = Bouquet.objects.filter(is_active=True).prefetch_related("events")
    return render(request, "catalog.html", {"bouquets": bouquets})


def card(request):
    return render(request, "card.html")


def consultation(request):
    return render(request, "consultation.html")
