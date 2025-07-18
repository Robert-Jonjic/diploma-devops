from django.db import models
from isbnlib import is_isbn10, is_isbn13
from django.core.exceptions import ValidationError


def validate_isbn(value):
    raw = value.replace("-", "").replace(" ", "")
    if not (is_isbn10(raw) or is_isbn13(raw)):
        raise ValidationError("Enter a valid ISBN-10 or ISBN-13.")


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=17, unique=True, validators=[validate_isbn])
    published_date = models.DateField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return f"{self.title} ({self.isbn})"
