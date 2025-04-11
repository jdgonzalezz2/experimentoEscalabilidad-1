from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from .logic import paciente_logic as pl

# Create your views here.

@csrf_exempt
def paciente_view(request):
    if request.method == 'GET':
        id = request.GET.get('id', None)
        if id:
            paciente, examenes_eeg, examenes_mri = pl.get_paciente(id)
            if paciente:
                response_data = {
                    'paciente': serializers.serialize('json', [paciente]),
                    'examenes_eeg': serializers.serialize('json', examenes_eeg),
                    'examenes_mri': serializers.serialize('json', examenes_mri)
                }
                return HttpResponse(json.dumps(response_data), 'application/json')
            return HttpResponse(json.dumps({'error': 'Paciente no encontrado'}), 
                              'application/json', status=404)
    
    if request.method == 'POST':
        paciente = pl.create_paciente(json.loads(request.body))
        return HttpResponse(serializers.serialize('json', [paciente]), 
                          'application/json', status=201)

@csrf_exempt
def examen_eeg_view(request):
    if request.method == 'POST':
        examen = pl.create_examen_eeg(json.loads(request.body))
        return HttpResponse(serializers.serialize('json', [examen]), 
                          'application/json', status=201)

@csrf_exempt
def examen_mri_view(request):
    if request.method == 'POST':
        examen = pl.create_examen_mri(json.loads(request.body))
        return HttpResponse(serializers.serialize('json', [examen]), 
                          'application/json', status=201)
