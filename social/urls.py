from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social.views import ProfileViewSet, PostViewSet

app_name = "social"

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profile")
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]
