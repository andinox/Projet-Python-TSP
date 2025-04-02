from django.db import models

class ICMP(models.Model):
    """
    This model keeps track of performed diagnostics.
    """
    STATUS_CHOICES = [
        ("Up", "Up"),
        ("Down", "Down"),
    ]

    destination = models.GenericIPAddressField()
    icmp_up_down_status = models.CharField(max_length=4, choices=STATUS_CHOICES, verbose_name="ICMP Status")
    date_test= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.destination} - {self.icmp_up_down_status} -{self.date_test} "
