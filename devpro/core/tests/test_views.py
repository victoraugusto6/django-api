from http import HTTPStatus

import pytest
from devpro.core.models import Author, Book
from django.shortcuts import resolve_url

CT_JSON = "application/json"

pytestmark = pytest.mark.django_db
list_authors_url = resolve_url("core:list-authors")


@pytest.fixture
def book(db):
    author = Author.objects.create(name="Luciano Ramalho")
    book = Book.objects.create(name="Python fluente", edition=2, publication_year=2023)
    book.authors.add(author)
    return book


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


def test_create_book(client):
    author = Author.objects.create(name="Luciano Ramalho")
    data = {
        "name": "Python fluente",
        "edition": 2,
        "publication_year": 2023,
        "authors": [author.id],
    }
    response = client.post("/api/books/", data=data, content_type=CT_JSON)

    assert response.status_code == HTTPStatus.CREATED
    book = Book.objects.first()
    assert response["Location"] == f"/api/books/{book.id}/"
    assert book is not None
    response_data = response.json()
    assert response_data["name"] == "Python fluente"
    assert response_data["edition"] == 2
    assert response_data["publication_year"] == 2023
    assert response_data["authors"] == [author.id]
    assert response_data["id"] == book.id


def test_read_book(client, book):
    response = client.get(f"/api/books/{book.id}/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book.to_dict()


def test_read_unexist_book(client):
    response = client.get("/api/books/10/")

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_book(client, book):
    author_2 = Author.objects.create(name="Renzo")
    data = {
        "id": book.id,
        "name": "Python fluente",
        "edition": 3,
        "publication_year": 2024,
        "authors": [author_2.pk],
    }

    response = client.put(f"/api/books/{book.id}/", data=data, content_type=CT_JSON)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == data


def test_put_unexist_book(client):
    response = client.put("/api/books/10/", data={}, content_type=CT_JSON)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_book(client, book):
    response = client.delete(f"/api/books/{book.id}/")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not Book.objects.filter(pk=book.pk).exists()


def test_delete_unexist_book(client):
    response = client.delete("/api/books/10/", content_type=CT_JSON)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_list_books(client, book):
    response = client.get("/api/books/")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"] == [book.to_dict()]


def test_filter_books_by_publication_year(client, book):
    author = Author.objects.create(name="David M. Beazley")
    book_2 = Book.objects.create(name="Python Cookbook", edition=1, publication_year=2016)
    book_2.authors.add(author)

    response = client.get("/api/books/", data={"publication_year": 2023})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"] == [book.to_dict()]


def test_filter_books_by_author(client, book):
    author = Author.objects.create(name="David M. Beazley")
    book_2 = Book.objects.create(name="Python Cookbook", edition=1, publication_year=2016)
    book_2.authors.add(author)

    response = client.get("/api/books/", data={"author": author.id})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"] == [book_2.to_dict()]


def test_filter_books_by_author_and_publication_year(client, book):
    author = Author.objects.create(name="David M. Beazley")
    book_2 = Book.objects.create(name="Python Cookbook", edition=1, publication_year=2016)
    book_2.authors.add(author)

    response = client.get("/api/books/", data={"author": author.id, "publication_year": book.publication_year})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["data"] == [book_2.to_dict(), book.to_dict()]
