from django.db import models
from core.models.security import Security


class SecurityScan(models.Model):
    security = models.ForeignKey(
        Security, on_delete=models.CASCADE, related_name="scans"
    )
    protocol = models.CharField(max_length=10)
    port = models.IntegerField()
    service_name = models.CharField(max_length=100)
    product = models.CharField(max_length=100, blank=True, null=True)
    version = models.CharField(max_length=100, blank=True, null=True)
    extrainfo = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return f"{self.security.hostname} - {self.protocol.upper()}/{self.port}"
