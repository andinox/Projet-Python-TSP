from django.db import models
from django.contrib.auth.models import User
from .interface import Interface_CONF, Interface_TEST
from django.utils.timezone import now
class ARP(models.Model):
    """
    This model represents ARP
    """
    timestamp = models.DateTimeField(auto_now_add=True)  
    # using abstract class to inherit the fields for the other classes that
    # we have two classes ARP_CONF & ARP_TEST to have the same fields
    class Meta:
        abstract= True

    def __str__(self):
        return f"IP: {self.ip_arp} - id: {self.idinterface}" 



class ARP_CONF(ARP):
    idinterface = models.ForeignKey(Interface_CONF, on_delete=models.CASCADE, related_name="arp_confs")
    ip_arp = models.GenericIPAddressField(verbose_name="IP ARP",primary_key=True)


class ARP_TEST(ARP):
    idinterface = models.ForeignKey(Interface_TEST, on_delete=models.CASCADE, related_name="arp_tests")
    ip_arp = models.GenericIPAddressField(verbose_name="IP ARP")



