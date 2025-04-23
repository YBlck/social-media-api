from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social.views import ProfileViewSet

app_name = "social"

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
