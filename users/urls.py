from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

# Create a router and register our viewset
router = DefaultRouter()
router.register(r"users", UserViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("api/", include(router.urls)),
]
