import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def profile_image_file_path(instance: "Profile", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profiles/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to=profile_image_file_path, null=True, blank=True
    )

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.full_name


class Follow(models.Model):
    follower = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.follower.full_name} follows {self.following.full_name}"


def post_media_file_path(instance: "Post", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    media = models.FileField(
        upload_to=post_media_file_path, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.profile.full_name} - {self.title}"
