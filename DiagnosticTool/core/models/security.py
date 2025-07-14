from django.db import models

class Security(models.Model):
    hostname = models.CharField(max_length=255)
    sys_descr = models.TextField()
    uptime = models.BigIntegerField()
    cdp_enabled = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.hostname})"