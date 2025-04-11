from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import pika


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

@csrf_exempt
def enviar_diagnostico(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='104.154.134.142',
                    credentials=pika.PlainCredentials('clinica_user', 'isis2503')
                )
            )
            channel = connection.channel()
            channel.basic_publish(
                exchange='clinica_exchange',
                routing_key='cambiar_diagnostico',
                body=json.dumps(data)
            )
            connection.close()
            return JsonResponse({'status': 'mensaje enviado'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'},status=405)