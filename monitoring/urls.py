from django.contrib import admin
from django.urls import path, include
from gestor_examenes import views as examenes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/examenes/', include('gestor_examenes.urls')),
    path('api/resultados/', include('gestor_resultados.urls')),
    path('api/enviar-diagnostico/', examenes_views.enviar_diagnostico)
] 