from django.db import models
from core.models.router import Router

class Diagnostic(models.Model):
    """
    This model keeps track of performed diagnostics.
    """
    router = models.ForeignKey(Router, on_delete=models.CASCADE)
    diagnosis_type = models.CharField(max_length=100)
    result = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.router.name} - {self.diagnosis_type}"
