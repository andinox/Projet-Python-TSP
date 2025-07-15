from django.db import models
from django.contrib.auth.models import User


class Router(models.Model):
    """
    This model represents a network router
    """

    name = models.CharField(max_length=100, verbose_name="Router Name")
    next_hop = models.GenericIPAddressField(verbose_name="Next Hop IP")
    users = models.ManyToManyField(User, verbose_name="Associated Users")

    def __str__(self):
        return f"{self.name}"
