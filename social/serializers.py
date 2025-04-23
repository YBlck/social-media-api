from rest_framework import serializers

from social.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user", "full_name", "bio", "country", "city", "image")
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
