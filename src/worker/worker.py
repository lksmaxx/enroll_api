import pika
import os
import json
import time
from pymongo import MongoClient

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "enroll_api_rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASS", "password")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "enrollment_queue")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin@enroll_api_mongo:27017/")
MONGO_DB = os.getenv("MONGO_DB", "enroll_api")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]

def connect_rabbitmq_with_retry(host, port, user, password, retries=10, delay=5):
    for i in range(retries):
        try:
            credentials = pika.PlainCredentials(user, password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, port=port, credentials=credentials)
            )
            return connection
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.ProbableAuthenticationError) as e:
            print(f"RabbitMQ não disponível, tentativa {i+1}/{retries}. Erro: {e}. Aguardando {delay}s...")
            time.sleep(delay)
    raise Exception("Não foi possível conectar ao RabbitMQ após várias tentativas.")

def process_enrollment(ch, method, properties, body):
    data = json.loads(body)
    enrollment_id = data["id"]
    print(f"Processando inscrição {enrollment_id}...")
    # Simula processamento
    time.sleep(2)
    # Atualiza status no MongoDB
    mongo_db.enrollments.update_one(
        {"_id": enrollment_id},
        {"$set": {"status": "processed", "message": "Inscrição processada com sucesso!"}}
    )
    print(f"Inscrição {enrollment_id} processada!")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = connect_rabbitmq_with_retry(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=process_enrollment)
    print("[WORKER] Aguardando inscrições...")
    channel.start_consuming()

if __name__ == "__main__":
    main() 