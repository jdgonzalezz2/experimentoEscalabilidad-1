
# Create your models here.
from django.db import models
from gestor_examenes.models import Paciente

class Diagnostico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=100, default="epilepsia refractaria")

    def __str__(self):
        return f"Diagnóstico de {self.paciente.nombre} - {self.tipo}"
