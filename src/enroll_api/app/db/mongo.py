from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config.config import config

# Variáveis globais para conexão
_client = None
_mongo_db = None

def get_mongo_client():
    """Obtém o cliente MongoDB, criando a conexão se necessário"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(config.MONGO_URI)
            # Verifica se a conexão está funcionando
            _client.admin.command('ping')
            print("Conexão com MongoDB estabelecida com sucesso!")
        except ConnectionFailure as e:
            print(f"Erro ao conectar ao MongoDB: {e}")
            raise
    return _client

def get_mongo_db():
    """Obtém o banco de dados MongoDB"""
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[config.MONGO_DB]
    return _mongo_db

# Para compatibilidade com código existente
@property
def mongo_db():
    return get_mongo_db()

# Cria um objeto que simula o comportamento anterior
class MongoDBProxy:
    @property
    def age_groups(self):
        return get_mongo_db().age_groups
    
    @property
    def enrollments(self):
        return get_mongo_db().enrollments

mongo_db = MongoDBProxy()
