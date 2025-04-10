#!/usr/bin/env python
import time
import pika
import json
import django
from sys import path
from os import environ

# Configuración de Django
path.append('monitoring/settings.py')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring.settings')
django.setup()

from gestor_examenes.models import Paciente
from gestor_resultados.models import Diagnostico

# Configuración de RabbitMQ
rabbit_host = 'host'
rabbit_user = 'clinica_user'
rabbit_password = 'isis2503'
exchange = 'clinica_exchange'
topic = 'cambiar_diagnostico'

# Configuración de replicación
NUM_REPLICAS = 3  # Número de réplicas deseadas

def setup_rabbitmq():
    # Configuración de reconexión
    connection_params = pika.ConnectionParameters(
        host=rabbit_host,
        credentials=pika.PlainCredentials(rabbit_user, rabbit_password),
        heartbeat=600,  # 10 minutos
        blocked_connection_timeout=300,  # 5 minutos
        retry_delay=5,  # 5 segundos entre reintentos
        connection_attempts=3  # Número de intentos de conexión
    )
    
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    # Configuración del exchange con alta disponibilidad
    channel.exchange_declare(
        exchange=exchange,
        exchange_type='topic',
        durable=True,
        auto_delete=False,
        internal=False,
        arguments={
            'alternate-exchange': f'{exchange}_alternate',  # Exchange alternativo para mensajes no enrutados
            'ha-mode': 'all',  # Alta disponibilidad para todos los nodos
            'ha-sync-mode': 'automatic'  # Sincronización automática
        }
    )
    
    return connection, channel

def enviar_diagnostico(channel, diagnostico):
    for i in range(NUM_REPLICAS):
        mensaje = {
            **diagnostico,
            'replica_id': i,
            'timestamp': time.time(),
            'message_id': f"{diagnostico['paciente_id']}_{i}_{int(time.time())}"
        }
        
        payload = json.dumps(mensaje)
        
        # Propiedades del mensaje con confirmación
        properties = pika.BasicProperties(
            delivery_mode=2,  # persistente
            content_type='application/json',
            content_encoding='utf-8',
            message_id=mensaje['message_id'],
            timestamp=int(time.time()),
            headers={
                'app_id': 'gestor_diagnosticos',
                'version': '1.0'
            }
        )
        
        # Envío con confirmación
        channel.confirm_delivery()
        try:
            channel.basic_publish(
                exchange=exchange,
                routing_key=topic,
                body=payload,
                properties=properties,
                mandatory=True  # Asegura que el mensaje sea enrutado
            )
            print(f"Diagnóstico confirmado para réplica {i} - Paciente {diagnostico['paciente_id']}")
        except pika.exceptions.UnroutableError:
            print(f"Error: Mensaje no pudo ser enrutado para réplica {i}")
        except pika.exceptions.NackError:
            print(f"Error: Broker rechazó el mensaje para réplica {i}")

def main():
    connection, channel = setup_rabbitmq()
    print('> Sistema de envío de diagnósticos iniciado')
    
    try:
        while True:
            pacientes = Paciente.objects.all()
            
            for paciente in pacientes:
                diagnostico = {
                    "paciente_id": paciente.id,
                    "descripcion": f"Actualización de diagnóstico para {paciente.nombre}",
                    "tipo": "epilepsia refractaria"
                }
                
                enviar_diagnostico(channel, diagnostico)
                time.sleep(2)
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nDeteniendo el productor...")
    except pika.exceptions.AMQPConnectionError:
        print("Error de conexión con el broker. Reintentando...")
        time.sleep(5)
        main()  # Reintentar conexión
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == "__main__":
    main()
