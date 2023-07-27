from django.db import models


class Lease(models.Model):

    class Meta():
        db_table = 'leases'

    mac = models.CharField(max_length=45, primary_key=True)
    ip = models.CharField(max_length=45)
    # A fines de saber a qué IP generar la consulta del agente SNMP, necesitamos tener vinculada la MAC address
    # a un IP.
    already_queried = models.BooleanField(default = False) 
    # El campo "already_queried" nos indica si el SNMP con un dado IP ya fue consultado en busca de cablemodems.


class CableModem(models.Model):

    class Meta():
        db_table = 'cm_models'

    vendor = models.CharField(max_length=128)
    model = models.CharField(max_length=45)
    software_version = models.CharField(max_length=45)
