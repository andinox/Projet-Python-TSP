from django.db import models
from core.models.routeur import Routeur

class Interface(models.Model):
    """
    Ce modèle permet d'enregister l'état des interfaces pour un routeur
    """
    routeur = models.ForeignKey(Routeur, on_delete=models.CASCADE)
    interface_name = models.CharField(max_length=100)
    admin_status = models.CharField(max_length=10)
    oper_status = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.interface_name, self.routeur.name , self.admin_status , self.oper_status