from django.db import models

class Routeur(models.Model):
    name = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name , self.ip

class Diagnostic(models.Model):
    """
    ce modèle permettra de garder les traces du diagnostic effectué
    """
    routeur = models.ForeignKey(Routeur, on_delete=models.CASCADE)
    type_diagno = models.CharField(max_length=100)
    resultat = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.routeur.name, self.type_diagno

class Scenario (models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.nom