from django.contrib.auth.models import User
from django.db import models


def profile_avatar_directory_path(instance: User, filename: str) -> str:
    return "users/user_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)
    bio = models.TextField(max_length=500, default="Here's my bio")
    agreement_accepted = models.BooleanField(default=False)
