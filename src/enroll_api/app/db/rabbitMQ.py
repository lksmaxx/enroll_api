from app.config.config import config
import pika
import time
import os

# Variáveis globais para conexão
_connection = None
_channel = None

def connect_rabbitmq_with_retry(host, port, retries=10, delay=5):
    """Conecta ao RabbitMQ com retry, tentando sem credenciais primeiro"""
    for i in range(retries):
        try:
            # Tenta primeiro sem credenciais (para desenvolvimento)
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=host, port=port, heartbeat=600, blocked_connection_timeout=300)
                )
                print(f"[API] Conectado ao RabbitMQ sem credenciais!")
                return connection
            except:
                # Se falhar, tenta com credenciais
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=host, 
                        port=port, 
                        credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD),
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                print(f"[API] Conectado ao RabbitMQ com credenciais!")
                return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ não disponível, tentativa {i+1}/{retries}. Aguardando {delay}s...")
            time.sleep(delay)
    raise Exception("Não foi possível conectar ao RabbitMQ após várias tentativas.")

def reset_connections():
    """Reseta as conexões globais"""
    global _connection, _channel
    try:
        if _channel and not _channel.is_closed:
            _channel.close()
    except:
        pass
    try:
        if _connection and not _connection.is_closed:
            _connection.close()
    except:
        pass
    _connection = None
    _channel = None

def get_rabbitmq_connection():
    """Obtém a conexão RabbitMQ, criando se necessário"""
    global _connection
    try:
        if _connection is None or _connection.is_closed:
            _connection = connect_rabbitmq_with_retry(config.RABBITMQ_HOST, config.RABBITMQ_PORT)
        return _connection
    except Exception as e:
        print(f"Erro ao obter conexão RabbitMQ: {e}")
        reset_connections()
        raise

def get_rabbitmq_channel():
    """Obtém o canal RabbitMQ, criando se necessário"""
    global _channel
    try:
        if _channel is None or _channel.is_closed:
            connection = get_rabbitmq_connection()
            _channel = connection.channel()
            _channel.queue_declare(queue=config.RABBITMQ_QUEUE, durable=True)
        return _channel
    except Exception as e:
        print(f"Erro ao obter canal RabbitMQ: {e}")
        reset_connections()
        raise

def publish_message(message):
    """Publica uma mensagem na fila com retry automático"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            channel = get_rabbitmq_channel()
            channel.basic_publish(
                exchange='', 
                routing_key=config.RABBITMQ_QUEUE, 
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # Torna a mensagem persistente
            )
            print(f"[API] Mensagem publicada com sucesso na tentativa {attempt + 1}")
            return
        except Exception as e:
            print(f"Erro ao publicar mensagem (tentativa {attempt + 1}/{max_retries}): {e}")
            reset_connections()
            if attempt == max_retries - 1:
                raise
            time.sleep(1)  # Aguarda antes de tentar novamente



