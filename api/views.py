from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer


class HealthViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"status": "ok"})


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # 201 + Location header
        response.status_code = status.HTTP_201_CREATED
        response["Location"] = f"{request.build_absolute_uri()}{response.data['id']}/"
        return response
