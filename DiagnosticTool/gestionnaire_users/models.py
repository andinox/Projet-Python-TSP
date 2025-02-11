# from django.contrib.auth.models import AbstractUser,Group
# from django.db import models
#
# # Create your models here.
# class User(AbstractUser):
#     ROLES=(("admin","Admin"),("user","User"))
#     role = models.CharField(max_length=10, choices=ROLES, default="user")
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         group, created = Group.objects.get_or_create(name=self.role)
#         self.groups.add(group)
