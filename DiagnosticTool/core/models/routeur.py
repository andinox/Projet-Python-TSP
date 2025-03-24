from django.db import models
from django.contrib.auth.models import User

class Routeur(models.Model):
    name = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    status = models.BooleanField(default=False)
    next_hop = models.GenericIPAddressField()
    as_bgp = models.IntegerField()
    utilisateur_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name , self.ip
