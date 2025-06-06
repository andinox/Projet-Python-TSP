from django.db import models
from .router import Router
class Interface(models.Model):
    """
    This model records the status of interfaces for a router
    """
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    interface_name = models.CharField(max_length=100)
    admin_status = models.CharField(max_length=10)
    reachability = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    subnet_mask = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True)

    class Meta:
        abstract= True

    def __str__(self):
        return f"{self.interface_name} - {self.router.name} (Admin: {self.admin_status}, Oper: {self.reachability}, Mask: {self.subnet_mask})"

class Interface_CONF(Interface):
    idinterface = models.IntegerField(primary_key=True)

class Interface_TEST(Interface):
    idinterface = models.IntegerField()
