from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social.models import Profile, Follow, Post
from social.permissions import IsAdminOrOwnerOrReadOnly
from social.serializers import (
    ProfileSerializer,
    ProfileCreateSerializer,
    ProfileListSerializer,
    FollowUnfollowSerializer,
    FollowersSerializer,
    FollowingSerializer,
    PostSerializer,
    PostCreateUpdateSerializer,
    PostListSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user").prefetch_related(
        "following", "followers"
    )
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
        if self.action in ["follow", "unfollow"]:
            return FollowUnfollowSerializer
        if self.action == "followers":
            return FollowersSerializer
        if self.action == "following":
            return FollowingSerializer
        return ProfileSerializer

    @action(
        detail=False,
        methods=["GET", "PUT", "PATCH"],
        url_path="me",
    )
    def profile(self, request):
        """Get the authenticated user's profile"""
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

    @action(
        detail=True, methods=["POST"], permission_classes=[IsAuthenticated]
    )
    def follow(self, request, pk=None):
        """Start following a user"""
        profile_to_follow = self.get_object()

        if not Profile.objects.filter(user=request.user).exists():
            return Response(
                {"message": "You have to create a profile first"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_follow = request.user.profile

        subscription = Follow.objects.filter(
            follower=user_to_follow, following=profile_to_follow
        ).first()

        if profile_to_follow == user_to_follow:
            return Response(
                {"message": "You can't follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if subscription:
            return Response(
                {
                    "message": f"You already follow {profile_to_follow.full_name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.create(
            follower=user_to_follow, following=profile_to_follow
        )
        return Response(
            {"message": f"You following {profile_to_follow.full_name}"},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True, methods=["POST"], permission_classes=[IsAuthenticated]
    )
    def unfollow(self, request, pk=None):
        """Stop following a user"""
        profile_to_unfollow = self.get_object()

        if not Profile.objects.filter(user=request.user).exists():
            return Response(
                {"message": "You have to create a profile first"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_unfollow = request.user.profile

        subscription = Follow.objects.filter(
            follower=user_to_unfollow, following=profile_to_unfollow
        ).first()

        if not subscription:
            return Response(
                {
                    "message": f"You don't follow {profile_to_unfollow.full_name}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()

        return Response(
            {"message": f"You unfollow {profile_to_unfollow.full_name}"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=True, methods=["GET"])
    def followers(self, request, pk=None):
        """List of all the user's followers"""
        profile = self.get_object()
        followers = profile.followers.select_related("follower__user")
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def following(self, request, pk=None):
        """List of all user subscriptions"""
        profile = self.get_object()
        following = profile.following.select_related("following__user")
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer
        return PostSerializer

    def create(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(profile=profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
