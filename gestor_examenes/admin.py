from django.contrib import admin

# Register your models here.
from gestor_examenes.models import Paciente, ExamenEEG, ExamenMRI

admin.site.register(Paciente)
admin.site.register(ExamenEEG)
admin.site.register(ExamenMRI)  
