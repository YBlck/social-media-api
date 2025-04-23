from rest_framework import viewsets

from social.models import Profile
from social.permissions import IsAdminOrOwnerOrReadOnly
from social.serializers import (
    ProfileSerializer,
    ProfileCreateSerializer,
    ProfileListSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return ProfileCreateSerializer
        if self.action == "list":
            return ProfileListSerializer

        return ProfileSerializer
