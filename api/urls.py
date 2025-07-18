from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, HealthViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")
router.register(r"", HealthViewSet, basename="health")   # /api/

urlpatterns = [path("", include(router.urls))]
