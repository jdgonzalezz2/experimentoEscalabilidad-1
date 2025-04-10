from django.db import models

# Create your models here.
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    identificacion = models.CharField(max_length=20, unique=True)
    edad = models.IntegerField()
    tipo_sangre = models.CharField(max_length=5, blank=True, null=True)
    alergias = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"

class ExamenEEG(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    archivo_eeg = models.FileField(upload_to="eeg/", blank=True, null=True)
    resultado = models.TextField(blank=True, null=True)

class ExamenMRI(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    archivo_mri = models.FileField(upload_to="mri/", blank=True, null=True)
    resultado = models.TextField(blank=True, null=True)

