from django.shortcuts import get_object_or_404, render

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


def bouquet_detail(request, slug):
    bouquet = get_object_or_404(Bouquet, slug=slug, is_active=True)
    return render(request, "card.html", {"bouquet": bouquet})
