from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Bouquet


@require_GET
def index(request):
    recommended_bouquets = (
        Bouquet.objects.filter(is_active=True)
        .prefetch_related("events")
        # TO-DO если букетов станет очень много лучше поменять чтоб не мучить БД
        .order_by("?")[:3]
    )
    return render(
        request,
        "index.html",
        {"recommended_bouquets": recommended_bouquets},
    )


@require_GET
def catalog(request):
    bouquets_list = Bouquet.objects.filter(is_active=True).prefetch_related("events")

    paginator = Paginator(bouquets_list, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "catalog.html", {"page_obj": page_obj})


@require_GET
def bouquet_detail(request, slug):
    bouquet = get_object_or_404(Bouquet, slug=slug, is_active=True)
    return render(request, "card.html", {"bouquet": bouquet})
