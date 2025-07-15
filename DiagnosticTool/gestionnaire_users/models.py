# models.py
from django.contrib.auth.models import User
from django.db import models


def user_avatar_path(instance, filename):
    return f"avatars/user_{instance.user.id}/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_avatar_path, default="default-avatar.png")

    def __str__(self):
        return self.user.username
