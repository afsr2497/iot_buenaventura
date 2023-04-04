from django.db import models

# Create your models here.
class estadoVehiculo(models.Model):
    registroTiempo = models.DateTimeField()
    registroInformacion = models.CharField(max_length=1,default="")