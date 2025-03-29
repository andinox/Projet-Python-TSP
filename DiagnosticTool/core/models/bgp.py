from django.db import models

class BGP(models.Model):
    """
    This model stores BGP session information
    """
    STATUS_CHOICES = [
        ("Up", "Up"),
        ("Down", "Down"),
    ]

    asn = models.IntegerField(verbose_name="Autonomous System Number") #helpful to understand as admin what the field stands for
    neighbor_ip = models.GenericIPAddressField(verbose_name="Neighbor IP Address")
    up_down_status = models.CharField(max_length=4, choices=STATUS_CHOICES, verbose_name="BGP Status")
    time_status = models.CharField(max_length=100, verbose_name="Time Since Last Status Change")

    def __str__(self):
        return f"{self.neighbor_ip} - ASN {self.asn}"
