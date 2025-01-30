from django.db import models

class Scenario(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=50)
    def __str__(self):
        return self.description