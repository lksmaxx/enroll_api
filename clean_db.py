import sys
import os

# Configuração para testes locais
os.environ["MONGO_HOST"] = "localhost"
os.environ["MONGO_PORT"] = "27017"

# Adiciona o path do src para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/enroll_api'))

from app.db.mongo import mongo_db

print("=== Limpando Banco de Dados ===")

# Limpa todas as coleções
result_age_groups = mongo_db.age_groups.delete_many({})
result_enrollments = mongo_db.enrollments.delete_many({})

print(f"Age groups removidos: {result_age_groups.deleted_count}")
print(f"Enrollments removidos: {result_enrollments.deleted_count}")

print("\n=== Verificando Estado Final ===")
print(f"Age groups restantes: {mongo_db.age_groups.count_documents({})}")
print(f"Enrollments restantes: {mongo_db.enrollments.count_documents({})}")

print("\nBanco de dados limpo com sucesso!") 