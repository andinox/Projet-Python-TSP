from django.contrib.auth.models import User
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
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagnostics', null=True)

    def __str__(self):
        user_display = self.created_by.username if self.created_by else "Utilisateur inconnu"
        return f"{self.router.name} - {self.diagnosis_type} - {user_display}"


    class Meta:
        """
        This class overrides the default Django Meta class to optimize SQL request
        """
        indexes = [
            models.Index(fields=['date']),
        ]
