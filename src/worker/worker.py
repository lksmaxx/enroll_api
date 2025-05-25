import pika
import os
import json
import time
from pymongo import MongoClient

# Configurações com defaults apropriados para teste e produção
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "enroll_api_rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASS", "password")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "enrollment_queue")

# Configuração do MongoDB - corrigida para usar o mesmo banco da aplicação
MONGO_HOST = os.getenv("MONGO_HOST", "enroll_api_mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")
MONGO_DB = os.getenv("MONGO_DB", "enrollment_db")  # Corrigido para usar o mesmo banco da aplicação

# Constrói URI do MongoDB baseado nas configurações
if MONGO_USERNAME and MONGO_PASSWORD:
    MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
else:
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

print(f"[WORKER] Configurações:")
print(f"  RabbitMQ: {RABBITMQ_USER}@{RABBITMQ_HOST}:{RABBITMQ_PORT}")
print(f"  MongoDB: {MONGO_URI}")
print(f"  Database: {MONGO_DB}")
print(f"  Queue: {RABBITMQ_QUEUE}")

# Variáveis globais para conexões (inicializadas posteriormente)
mongo_client = None
mongo_db = None

def connect_mongodb():
    """Conecta ao MongoDB com configuração dinâmica"""
    global mongo_client, mongo_db
    
    try:
        print("[WORKER] Conectando ao MongoDB...")
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_db = mongo_client[MONGO_DB]
        # Testa a conexão
        mongo_client.admin.command('ping')
        print("[WORKER] MongoDB conectado com sucesso!")
        return True
    except Exception as e:
        print(f"[WORKER] Erro ao conectar MongoDB: {e}")
        return False

def connect_rabbitmq_with_retry(host, port, user, password, retries=15, delay=5):
    """Conecta ao RabbitMQ com retry e logs detalhados"""
    for i in range(retries):
        try:
            print(f"[WORKER] Tentativa {i+1}/{retries} de conexão ao RabbitMQ...")
            
            # Tenta primeiro sem credenciais (para desenvolvimento)
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=host, port=port)
                )
                print(f"[WORKER] Conectado ao RabbitMQ sem credenciais!")
                return connection
            except:
                # Se falhar, tenta com credenciais
                credentials = pika.PlainCredentials(user, password)
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=host, port=port, credentials=credentials)
                )
                print(f"[WORKER] Conectado ao RabbitMQ com credenciais!")
                return connection
                
        except Exception as e:
            print(f"[WORKER] Falha na tentativa {i+1}: {e}")
            if i < retries - 1:
                print(f"[WORKER] Aguardando {delay}s antes da próxima tentativa...")
                time.sleep(delay)
    
    raise Exception(f"[WORKER] Não foi possível conectar ao RabbitMQ após {retries} tentativas.")

def process_enrollment(ch, method, properties, body):
    """Processa uma inscrição da fila"""
    try:
        # Verifica se o body não está vazio
        if not body:
            print(f"[WORKER] Mensagem vazia recebida, descartando...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Tenta decodificar como string primeiro
        try:
            body_str = body.decode('utf-8') if isinstance(body, bytes) else str(body)
            if not body_str.strip():
                print(f"[WORKER] Mensagem vazia após decodificação, descartando...")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
        except Exception as e:
            print(f"[WORKER] Erro ao decodificar mensagem: {e}, descartando...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Tenta fazer parse do JSON
        try:
            data = json.loads(body_str)
        except json.JSONDecodeError as e:
            print(f"[WORKER] JSON inválido recebido: {e}")
            print(f"[WORKER] Conteúdo da mensagem: {body_str[:100]}...")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Descarta mensagem inválida
            return
        
        # Verifica se tem os campos necessários
        if not isinstance(data, dict) or "id" not in data:
            print(f"[WORKER] Mensagem sem campo 'id' obrigatório: {data}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        enrollment_id = data["id"]
        print(f"[WORKER] Processando inscrição {enrollment_id}...")
        
        # Verifica se o enrollment existe no banco antes de processar
        existing_enrollment = mongo_db.enrollments.find_one({"_id": enrollment_id})
        if not existing_enrollment:
            print(f"[WORKER] Inscrição {enrollment_id} não encontrada no banco - pode ter sido removida ou ser de teste antigo")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Descarta mensagem órfã
            return
        
        # Verifica se já foi processada
        if existing_enrollment.get("status") == "processed":
            print(f"[WORKER] Inscrição {enrollment_id} já foi processada anteriormente")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        print(f"[WORKER] Iniciando processamento da inscrição {enrollment_id} (nome: {existing_enrollment.get('name', 'N/A')})")
        
        # Simula processamento (mínimo 2s conforme requisito)
        time.sleep(2)
        
        # Atualiza status no MongoDB
        result = mongo_db.enrollments.update_one(
            {"_id": enrollment_id},
            {"$set": {"status": "processed", "message": "Inscrição processada com sucesso!"}}
        )
        
        if result.modified_count > 0:
            print(f"[WORKER] ✅ Inscrição {enrollment_id} processada com sucesso!")
        else:
            print(f"[WORKER] ⚠️ Falha ao atualizar status da inscrição {enrollment_id}")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"[WORKER] ❌ Erro inesperado ao processar inscrição: {e}")
        print(f"[WORKER] Tipo do body: {type(body)}")
        print(f"[WORKER] Conteúdo do body: {body}")
        # Rejeita a mensagem sem recolocar para evitar loop infinito
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    """Função principal do worker"""
    try:
        print("[WORKER] Iniciando worker...")
        
        # Conecta ao MongoDB primeiro
        if not connect_mongodb():
            raise Exception("Falha ao conectar ao MongoDB")
        
        # Conecta ao RabbitMQ
        connection = connect_rabbitmq_with_retry(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD)
        channel = connection.channel()
        
        # Declara a fila (garante que existe)
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        
        # Configura QoS para processar uma mensagem por vez
        channel.basic_qos(prefetch_count=1)
        
        # Configura o consumidor
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=process_enrollment)
        
        print(f"[WORKER] Aguardando inscrições na fila '{RABBITMQ_QUEUE}'...")
        print("[WORKER] Para parar, pressione CTRL+C")
        
        # Inicia o consumo
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print("[WORKER] Parando worker...")
        if 'channel' in locals():
            channel.stop_consuming()
        if 'connection' in locals():
            connection.close()
        if mongo_client:
            mongo_client.close()
    except Exception as e:
        print(f"[WORKER] Erro fatal: {e}")
        raise

if __name__ == "__main__":
    main() 