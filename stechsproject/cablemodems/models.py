from django.db import models


class Lease(models.Model):

    class Meta():
        db_table = 'leases'

    mac = models.CharField(max_length=45, primary_key=True)
    ip = models.CharField(max_length=45)
    already_queried = models.BooleanField(default = False)

class CableModem(models.Model):

    class Meta():
        db_table = 'cm_models'

    vendor = models.CharField(max_length=128)
    model = models.CharField(max_length=45)
    software_version = models.CharField(max_length=45)
