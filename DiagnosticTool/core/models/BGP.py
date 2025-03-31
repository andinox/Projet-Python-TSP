from django.db import models

class BGP(models.Model):
    STATUS_CHOICES = [
    ("Up", "Up"),
    ("Down", "Down"),
    ]

    ASN = models.IntegerField()
    NeighborIP = models.GenericIPAddressField()
    Up_down_status = models.CharField(max_length=4, choices=STATUS_CHOICES )
    timeStatus = models.CharField(max_length=100)  

    def __str__(self):
        return f"{self.NeighborIP} - ASN {self.ASN}"
