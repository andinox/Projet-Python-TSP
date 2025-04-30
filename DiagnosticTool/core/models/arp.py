from django.db import models
from django.contrib.auth.models import User
from .interface import Interface_CONF, Interface_TEST

class ARP(models.Model):
    """
    This model represents ARP
    """
    ip_arp = models.GenericIPAddressField(verbose_name="IP ARP",primary_key=True)

    # using abstract class to inherit the fields for the other classes that
    # we have two classes ARP_CONF & ARP_TEST to have the same fields
    class Meta:
        abstract= True

    def __str__(self):
        return f"IP: {self.ip_arp} - id: {self.idinterface}" 



class ARP_CONF(ARP):
    idinterface = models.ForeignKey(Interface_CONF, on_delete=models.CASCADE)


class ARP_TEST(ARP):
    idinterface = models.ForeignKey(Interface_TEST, on_delete=models.CASCADE)


