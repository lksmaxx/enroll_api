from app.config.config import config
import pika
import time
import os

def connect_rabbitmq_with_retry(host, port, retries=10, delay=5):
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)))
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ não disponível, tentativa {i+1}/{retries}. Aguardando {delay}s...")
            time.sleep(delay)
    raise Exception("Não foi possível conectar ao RabbitMQ após várias tentativas.")

connection = connect_rabbitmq_with_retry(config.RABBITMQ_HOST, config.RABBITMQ_PORT)
channel = connection.channel()

channel.queue_declare(queue=config.RABBITMQ_QUEUE, durable=True)

def publish_message(message):
    channel.basic_publish(exchange='', routing_key=config.RABBITMQ_QUEUE, body=message)



