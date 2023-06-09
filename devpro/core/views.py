import json
from http import HTTPStatus

from devpro.core.models import Author, Book
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, resolve_url

DEFAULT_PAGE_SIZE = 25


def page2dict(page):
    return {
        "data": [a.to_dict() for a in page],
        "count": page.paginator.count,
        "current_page": page.number,
        "num_pages": page.paginator.num_pages,
    }


def authors(request):
    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", DEFAULT_PAGE_SIZE)
    q = request.GET.get("q")

    queryset = Author.objects.all()
    if q:
        queryset = queryset.filter(name__icontains=q)

    paginator = Paginator(queryset, per_page=page_size)
    page = paginator.get_page(page_number)

    return JsonResponse(page2dict(page))


def book_list_create(request):
    if request.method == "POST":
        payload = json.load(request)
        authors = payload.pop("authors")

        book = Book.objects.create(**payload)
        book.authors.set(authors)

        data = book.to_dict()
        response = JsonResponse(data, status=HTTPStatus.CREATED)
        response["Location"] = resolve_url(book)

        return response
    else:
        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", DEFAULT_PAGE_SIZE)

        filters = Q()

        if publication_year := request.GET.get("publication_year"):
            filters |= Q(publication_year=publication_year)

        if author_id := request.GET.get("author"):
            filters |= Q(authors=author_id)

        queryset = Book.objects.filter(filters)
        paginator = Paginator(queryset, per_page=page_size)
        page = paginator.get_page(page_number)

        return JsonResponse(page2dict(page))


def book_read_update_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)

    handlers = {
        "GET": _book_read,
        "PUT": _book_update,
        "DELETE": _book_delete,
    }

    try:
        handler = handlers[request.method]
    except KeyError:
        return HttpResponseNotAllowed()

    return handler(request, book)


def _book_read(request, book):
    return JsonResponse(book.to_dict())


def _book_update(request, book):
    payload = json.load(request)
    book.name = payload["name"]
    book.edition = payload["edition"]
    book.publication_year = payload["publication_year"]
    book.authors.set(payload["authors"])
    book.save()

    return JsonResponse(book.to_dict())


def _book_delete(request, book):
    book.delete()
    return HttpResponse(status=HTTPStatus.NO_CONTENT)
