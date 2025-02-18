from django.db import models
from django.utils.text import slugify

class Scenario(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(default="", null=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nom