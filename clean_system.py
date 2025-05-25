#!/usr/bin/env python3
"""
Script para limpar completamente o sistema de enrollment
Remove todos os dados do MongoDB e mensagens da fila RabbitMQ
"""

import sys
import os

# Adiciona o diretório de testes ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

from conftest import clean_db

if __name__ == "__main__":
    print("🧹 Limpando sistema de enrollment...")
    print("=" * 50)
    
    try:
        clean_db()
        print("=" * 50)
        print("✅ Sistema limpo com sucesso!")
        print("   - MongoDB: Todas as coleções limpas")
        print("   - RabbitMQ: Fila purgada")
        print("   - Worker: Não deve mais processar mensagens órfãs")
    except Exception as e:
        print("=" * 50)
        print(f"❌ Erro ao limpar sistema: {e}")
        sys.exit(1) 