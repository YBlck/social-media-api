from rest_framework import serializers

from social.models import Profile, Follow, Post


class ProfileSerializer(serializers.ModelSerializer):
    followers = serializers.IntegerField(
        read_only=True, source="followers.count"
    )
    following = serializers.IntegerField(
        read_only=True, source="following.count"
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "full_name",
            "bio",
            "country",
            "city",
            "image",
            "followers",
            "following",
        )
        read_only_fields = ("id", "user", "full_name")


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "bio", "country", "city", "image")

    def create(self, validated_data):
        user = validated_data["user"]
        if Profile.objects.filter(user=user.id).exists():
            raise serializers.ValidationError("You already have a profile")
        profile = Profile.objects.create(**validated_data)
        return profile


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "full_name", "country", "city", "image")


class FollowUnfollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")
        read_only_fields = ("id", "follower", "following", "created_at")


class FollowersSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="follower.full_name", read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "name")


class FollowingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="following.full_name", read_only=True)

    class Meta:
        model = Follow
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "profile", "title", "content", "media", "created_at")


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "content", "media")


class PostListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="profile.full_name", read_only=True)

    class Meta:
     model = Post
     fields = ("id", "user", "title", "created_at")
