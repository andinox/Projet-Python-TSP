from django.db import models
from django.contrib.auth.models import User

class ARP(models.Model):
    """
    This model represents ARP
    """
    ip_arp = models.GenericIPAddressField(verbose_name="IP ARP",primary_key=True)
    def __str__(self):
        return f"{self.ip_arp}"
