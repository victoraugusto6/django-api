from devpro.core.models import Author
from django.core.paginator import Paginator
from django.http import JsonResponse

DEFAULT_PAGE_SIZE = 25


def authors(request):
    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", DEFAULT_PAGE_SIZE)
    q = request.GET.get("q")

    queryset = Author.objects.all()
    if q:
        queryset = queryset.filter(name__icontains=q)

    paginator = Paginator(queryset, per_page=page_size)
    page = paginator.get_page(page_number)

    return JsonResponse(
        {
            "data": [a.to_dict() for a in page.object_list],
            "count": paginator.count,
            "current_page": int(page_number),
            "num_pages": paginator.num_pages,
        }
    )
