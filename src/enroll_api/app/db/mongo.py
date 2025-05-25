from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config.config import config

try:
    client = MongoClient(config.MONGO_URI)
    # Verifica se a conexão está funcionando
    client.admin.command('ping')
    db = client[config.MONGO_DB]
    print("Conexão com MongoDB estabelecida com sucesso!")
except ConnectionFailure as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
    raise
