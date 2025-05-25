import os

class Config:
    MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    MONGO_HOST = os.getenv("MONGO_HOST", "enroll_api_mongo")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DB = os.getenv("MONGO_DB", "enroll_api")
    
    # Constrói URI com ou sem autenticação
    if MONGO_USERNAME and MONGO_PASSWORD:
        MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
    else:
        MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "enroll_api_rabbitmq")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "enrollment_queue")    
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")

    # Basic Auth Configuration
    # Caminho para o arquivo de usuários (relativo ao diretório da aplicação)
    USERS_FILE_PATH = os.getenv("USERS_FILE_PATH", "app/config/users.json")
    
    # Fallback para variáveis de ambiente (caso o arquivo não exista)
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME", "admin")
    BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD", "secret123")
    
    # Configuração para usuários múltiplos (formato: user1:pass1,user2:pass2)
    BASIC_AUTH_USERS = os.getenv("BASIC_AUTH_USERS", "admin:secret123,config:config123")


config = Config()