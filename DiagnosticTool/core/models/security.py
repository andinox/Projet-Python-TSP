from django.db import models

class Security(models.Model):
    hostname = models.CharField(max_length=255)  # sysName
    sys_descr = models.TextField()               # sysDescr
    uptime = models.BigIntegerField()            # sysUptime
    cdp_enabled = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.hostname})"