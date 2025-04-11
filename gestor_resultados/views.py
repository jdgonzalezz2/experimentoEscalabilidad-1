from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from .logic import diagnostico_logic as dl

@csrf_exempt
def diagnostico_view(request):
    if request.method == 'GET':
        paciente_id = request.GET.get('paciente_id', None)
        if paciente_id:
            paciente, diagnosticos = dl.get_diagnosticos_paciente(paciente_id)
            if paciente:
                response_data = {
                    'paciente': serializers.serialize('json', [paciente]),
                    'diagnosticos': serializers.serialize('json', diagnosticos)
                }
                return HttpResponse(json.dumps(response_data), 'application/json')
            return HttpResponse(json.dumps({'error': 'Paciente no encontrado'}), 
                              'application/json', status=404)
    
    if request.method == 'POST':
        diagnostico = dl.create_diagnostico(json.loads(request.body))
        return HttpResponse(serializers.serialize('json', [diagnostico]), 
                          'application/json', status=201)

@csrf_exempt
def enviar_diagnostico(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Diagnóstico recibido:", data)
        return JsonResponse({"status": "mensaje enviado"})
    else:
        return JsonResponse({"error": "Método no permitido"},status=405)