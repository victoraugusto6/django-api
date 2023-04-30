from http import HTTPStatus

import pytest
from devpro.core.models import Author
from django.shortcuts import resolve_url

pytestmark = pytest.mark.django_db
list_authors_url = resolve_url("core:list-authors")


def test_list_all_authors(client):
    Author.objects.bulk_create(Author(name=f"Author {i}") for i in range(10))

    response = client.get(list_authors_url, data={"page": 2, "page_size": 5})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["num_pages"] == 2
    assert [a["name"] for a in response.json()["data"]] == [f"Author {a}" for a in range(5, 10)]


def test_search_authors_by_name(client):
    author_1 = Author.objects.create(name="Guido Van Rossum")
    Author.objects.create(name="Luciano Ramalho")

    response = client.get(list_authors_url, data={"q": "rossum"})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"] == [{"id": author_1.id, "name": "Guido Van Rossum"}]


def test_search_authors_by_name_without_match(client):
    Author.objects.create(name="Guido Van Rossum")

    response = client.get(list_authors_url, data={"q": "no match"})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"] == []
