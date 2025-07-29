from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Book


class BookViewTest(APITestCase):
    """Verify book listing returns expected data."""

    def test_list_contains_created_book(self):
        book = Book.objects.create(
            title="Demo",
            description="Description",
            author="Author",
            isbn="9781234567897",
            published_date=date.today(),
        )

        url = reverse("api:book-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = response.json()
        results = payload["results"] if "results" in payload else payload

        self.assertEqual(len(results), 1)
        returned = results[0]
        self.assertEqual(returned["title"], book.title)
        self.assertEqual(returned["description"], book.description)
        self.assertEqual(returned["author"], book.author)


class HealthViewTest(APITestCase):
    """Ensure the health-check endpoint responds with status OK."""

    def test_health_endpoint(self):
        url = reverse("api:health-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "ok")


class BookCrudExtraTests(APITestCase):
    """Additional CRUD and validation scenarios."""

    def _create_book(self, **overrides) -> Book:
        data = dict(
            title="Sample",
            description="Sample description",
            author="Author One",
            isbn="9780000000001",
            published_date=date.today(),
        )
        data.update(overrides)
        return Book.objects.create(**data)

    def test_update_book_title(self):
        """PATCH updates the book title."""
        book = self._create_book()
        url = reverse("api:book-detail", args=[book.id])

        response = self.client.patch(url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.title, "Updated")

    def test_delete_book(self):
        """DELETE removes the book record."""
        book = self._create_book()
        url = reverse("api:book-detail", args=[book.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_duplicate_isbn_rejected(self):
        """POST with an existing ISBN returns 400."""
        self._create_book(isbn="9789999999999")

        url = reverse("api:book-list")
        duplicate = {
            "title": "Dup ISBN",
            "author": "Author Two",
            "isbn": "9789999999999",
            "published_date": date.today().isoformat(),
            "description": "Should fail",
        }
        response = self.client.post(url, duplicate, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("isbn", response.data)
