from django.urls import path
from . import views

urlpatterns = [
    path('paciente/', views.paciente_view, name='paciente'),
    path('examen-eeg/', views.examen_eeg_view, name='examen_eeg'),
    path('examen-mri/', views.examen_mri_view, name='examen_mri'),
    path('api/enviar-diagnostico/', views.enviar_diagnostico)
] 