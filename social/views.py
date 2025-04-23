from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

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

    def get_queryset(self):
        """Profile filtering by user first or last name, country or city"""
        name = self.request.query_params.get("name")
        country = self.request.query_params.get("country")
        city = self.request.query_params.get("city")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(
                Q(user__first_name__icontains=name)
                | Q(user__last_name__icontains=name)
            )
        if country:
            queryset = queryset.filter(country__icontains=country)
        if city:
            queryset = queryset.filter(city__icontains=city)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return ProfileCreateSerializer
        if self.action == "list":
            return ProfileListSerializer
        return ProfileSerializer

    @action(
        detail=False,
        methods=["GET", "PUT", "PATCH"],
        url_path="me",
    )
    def profile(self, request):
        """Endpoint to get the authenticated user's profile"""
        profile = get_object_or_404(Profile, user=request.user)

        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(
                profile, data=request.data, partial=(request.method == "PATCH")
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
