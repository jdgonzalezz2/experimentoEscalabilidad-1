from ..models import Paciente, ExamenEEG, ExamenMRI

def get_paciente(id):
    try:
        paciente = Paciente.objects.get(id=id)
        examenes_eeg = ExamenEEG.objects.filter(paciente=paciente)
        examenes_mri = ExamenMRI.objects.filter(paciente=paciente)
        return paciente, examenes_eeg, examenes_mri
    except Paciente.DoesNotExist:
        return None, None, None

def create_paciente(data):
    paciente = Paciente.objects.create(
        nombre=data.get('nombre'),
        identificacion=data.get('identificacion'),
        edad=data.get('edad'),
        tipo_sangre=data.get('tipo_sangre'),
        alergias=data.get('alergias')
    )
    return paciente

def create_examen_eeg(data):
    paciente = Paciente.objects.get(id=data.get('paciente_id'))
    examen = ExamenEEG.objects.create(
        paciente=paciente,
        fecha=data.get('fecha'),
        archivo_eeg=data.get('archivo_eeg'),
        resultado=data.get('resultado')
    )
    return examen

def create_examen_mri(data):
    paciente = Paciente.objects.get(id=data.get('paciente_id'))
    examen = ExamenMRI.objects.create(
        paciente=paciente,
        fecha=data.get('fecha'),
        archivo_mri=data.get('archivo_mri'),
        resultado=data.get('resultado')
    )
    return examen 