from django.urls import path
from . import views

urlpatterns = [
    path('diagnostico/', views.diagnostico_view, name='diagnostico'),
] 