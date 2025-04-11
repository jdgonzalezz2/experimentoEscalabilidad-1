from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/examenes/', include('gestor_examenes.urls')),
    path('api/resultados/', include('gestor_resultados.urls')),
] 