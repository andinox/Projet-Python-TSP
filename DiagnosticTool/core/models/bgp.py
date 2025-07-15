from django.db import models
from django.utils import timezone
from .router import Router


class BGP(models.Model):
    """
    This model stores BGP session information
    """

    STATUS_CHOICES = [
        ("Up", "Up"),
        ("Down", "Down"),
    ]
    router = models.ForeignKey(Router, null=True, on_delete=models.CASCADE)
    neighbor_ip = models.GenericIPAddressField(verbose_name="Neighbor IP Address")
    asn = models.IntegerField(verbose_name="Autonomous System Number")
    up_down_status = models.CharField(
        max_length=4, choices=STATUS_CHOICES, verbose_name="BGP Status"
    )
    time_last_change = models.CharField(
        max_length=100, verbose_name="Time Since Last Status Change"
    )
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Timestamp")

    class Meta:
        abstract = True

    def __str__(self):
        return f"ASN {self.asn}"


class BGP_CONF(BGP):
    neighbor_ip = models.GenericIPAddressField(
        verbose_name="Neighbor IP Address", primary_key=True
    )
    router = models.ForeignKey(
        Router, null=True, on_delete=models.CASCADE, related_name="bgp_confs"
    )

    def __str__(self):
        return f"[CONF] {self.neighbor_ip} - ASN {self.asn}"


class BGP_TEST(BGP):
    router = models.ForeignKey(
        Router, null=True, on_delete=models.CASCADE, related_name="bgp_tests"
    )

    def __str__(self):
        return f"[TEST] {self.neighbor_ip} - ASN {self.asn}"
