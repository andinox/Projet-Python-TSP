from django.db import models
from django.contrib.auth.models import User
from .interface import Interface

class ARP(models.Model):
    """
    This model represents ARP
    """
    ip_arp = models.GenericIPAddressField(verbose_name="IP ARP",primary_key=True)
    idinterface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    def __str__(self):
        return f"IP: {self.ip_arp} - id: {self.idinterface}" 
