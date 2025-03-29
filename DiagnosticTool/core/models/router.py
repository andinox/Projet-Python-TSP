from django.db import models
from django.contrib.auth.models import User

class Router(models.Model):
    """
    This model represents a network router
    """
    name = models.CharField(max_length=100, verbose_name="Router Name")
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    status = models.BooleanField(default=False, verbose_name="Operational Status")
    next_hop = models.GenericIPAddressField(verbose_name="Next Hop IP")
    as_bgp = models.IntegerField(verbose_name="BGP Autonomous System Number")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Associated User")

    def __str__(self):
        return f"{self.name} - {self.ip_address}"
