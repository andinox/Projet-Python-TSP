from django.db import models
from .router import Router


class BGP(models.Model):
    """
    This model stores BGP session information
    """
    STATUS_CHOICES = [
        ("Up", "Up"),
        ("Down", "Down"),
    ]
    router = models.ForeignKey(Router,null=True, on_delete=models.CASCADE)
    asn = models.IntegerField(verbose_name="Autonomous System Number") #helpful to understand as admin what the field stands for
    neighbor_ip = models.GenericIPAddressField(verbose_name="Neighbor IP Address", primary_key=True)
    up_down_status = models.CharField(max_length=4, choices=STATUS_CHOICES, verbose_name="BGP Status")
    time_last_change = models.CharField(max_length=100, verbose_name="Time Since Last Status Change")

    def __str__(self):
        return f"{self.neighbor_ip} - ASN {self.asn}"

