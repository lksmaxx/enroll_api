import os

class Config:
    MONGO_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
    MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "admin")
    MONGO_HOST = os.getenv("MONGO_HOST", "enroll_api_mongo")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DB = os.getenv("MONGO_DB", "enroll_api")
    
    MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "enroll_api_rabbitmq")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "enrollment_queue")    
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")



config = Config()