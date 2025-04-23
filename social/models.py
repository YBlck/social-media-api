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
    bio = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(
        upload_to=profile_image_file_path, null=True, blank=True
    )

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.full_name
