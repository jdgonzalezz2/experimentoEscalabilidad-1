import json
import pika
from sys import path
from os import environ
import django
import time
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de Django
path.append('monitoring/settings.py')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring.settings')
django.setup()

from gestor_resultados.models import Diagnostico
from gestor_examenes.models import Paciente

# Configuración de RabbitMQ
rabbit_host = '104.154.134.142'
rabbit_user = 'clinica_user'
rabbit_password = 'isis2503'
exchange = 'clinica_exchange'
topic = 'cambiar_diagnostico'

# Configuración de replicación
REPLICA_ID = 0  # Identificador único para esta réplica

def setup_rabbitmq():
    # Configuración de reconexión
    connection_params = pika.ConnectionParameters(
        host=rabbit_host,
        credentials=pika.PlainCredentials(rabbit_user, rabbit_password),
        heartbeat=600,
        blocked_connection_timeout=300,
        retry_delay=5,
        connection_attempts=3
    )
    
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    # Configuración del exchange
    channel.exchange_declare(
        exchange=exchange,
        exchange_type='topic',
        durable=True,
        auto_delete=False,
        internal=False,
        arguments={
            'alternate-exchange': f'{exchange}_alternate',
            'ha-mode': 'all',
            'ha-sync-mode': 'automatic'
        }
    )
    
    # Configuración de la cola
    queue_name = f'diagnosticos_replica_{REPLICA_ID}'
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        exclusive=False,
        auto_delete=False,
        arguments={
            'x-message-ttl': 86400000,  # 24 horas en milisegundos
            'x-max-length': 10000,  # Máximo número de mensajes
            'x-overflow': 'reject-publish',  # Rechazar nuevos mensajes si se excede el límite
            'x-dead-letter-exchange': f'{exchange}_dlx',  # Exchange para mensajes muertos
            'x-dead-letter-routing-key': f'dlq.{queue_name}'  # Routing key para mensajes muertos
        }
    )
    
    # Vincular la cola al exchange
    channel.queue_bind(
        exchange=exchange,
        queue=queue_name,
        routing_key=topic
    )
    
    return connection, channel, queue_name

def procesar_diagnostico(payload):
    try:
        paciente_id = payload.get('paciente_id')
        descripcion = payload.get('descripcion')
        tipo = payload.get('tipo', 'epilepsia refractaria')
        replica_id = payload.get('replica_id')
        timestamp = payload.get('timestamp')
        message_id = payload.get('message_id')
        
        if replica_id != REPLICA_ID:
            logger.info(f"Mensaje ignorado - Destinado a réplica {replica_id}")
            return
        
        paciente = Paciente.objects.get(id=paciente_id)
        
        diagnostico = Diagnostico(
            paciente=paciente,
            descripcion=descripcion,
            tipo=tipo
        )
        diagnostico.save()
        
        logger.info(f"Diagnóstico procesado - ID: {message_id} - Paciente: {paciente.nombre}")
        logger.info(f"Timestamp: {time.ctime(timestamp)}")
        
    except Paciente.DoesNotExist:
        logger.error(f"Paciente no encontrado - ID: {paciente_id}")
    except Exception as e:
        logger.error(f"Error al procesar mensaje {message_id}: {str(e)}")
        raise

def main():
    connection, channel, queue_name = setup_rabbitmq()
    logger.info(f'Réplica {REPLICA_ID} iniciada. Esperando diagnósticos...')

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode('utf8'))
            procesar_diagnostico(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    # Configuración del consumidor
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False  # Desactivar auto-ack para manejo manual
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("\nDeteniendo la réplica...")
    except pika.exceptions.AMQPConnectionError:
        logger.error("Error de conexión con el broker. Reintentando...")
        time.sleep(5)
        main()  # Reintentar conexión
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == "__main__":
    main()