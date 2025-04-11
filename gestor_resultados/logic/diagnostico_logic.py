from ..models import Diagnostico
from gestor_examenes.models import Paciente

def get_diagnosticos_paciente(paciente_id):
    try:
        paciente = Paciente.objects.get(id=paciente_id)
        diagnosticos = Diagnostico.objects.filter(paciente=paciente)
        return paciente, diagnosticos
    except Paciente.DoesNotExist:
        return None, None

def create_diagnostico(data):
    paciente = Paciente.objects.get(id=data.get('paciente_id'))
    diagnostico = Diagnostico.objects.create(
        paciente=paciente,
        descripcion=data.get('descripcion'),
        tipo=data.get('tipo', 'epilepsia refractaria')
    )
    return diagnostico 