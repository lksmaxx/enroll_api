#!/usr/bin/env python3
"""
Script para executar testes do sistema de enrollment de forma organizada.
"""

import subprocess
import sys
import os
import argparse
import time
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Executa um comando e retorna True se bem-sucedido"""
    print(f"\n🔄 {description}")
    print(f"Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FALHOU")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False


def check_environment() -> bool:
    """Verifica se o ambiente está pronto para os testes"""
    print("🔍 Verificando ambiente...")
    
    # Verificar se pytest está instalado
    try:
        subprocess.run(["pytest", "--version"], capture_output=True, check=True)
        print("✅ pytest instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest não encontrado. Instale com: pip install pytest")
        return False
    
    # Verificar se a API está rodando
    try:
        import requests
        response = requests.get(os.getenv("ENROLL_API_URL", "http://localhost:8000/"), timeout=5) 
        if response.status_code == 200:
            print("✅ API está rodando")
        else:
            print(f"⚠️ API respondeu com status {response.status_code}")
    except Exception as e:
        print(f"❌ API não está acessível: {e}")
        print("Execute 'docker compose up -d' para iniciar o ambiente")
        return False
    
    return True


def run_unit_tests() -> bool:
    """Executa testes unitários"""
    cmd = ["pytest", "tests/test_unit.py", "-v", "--tb=short"]
    return run_command(cmd, "Testes Unitários")


def run_auth_tests() -> bool:
    """Executa testes de autenticação"""
    cmd = ["pytest", "tests/test_auth.py", "-v", "--tb=short"]
    return run_command(cmd, "Testes de Autenticação")


def run_admin_tests() -> bool:
    """Executa testes administrativos"""
    cmd = ["pytest", "tests/test_admin.py", "-v", "--tb=short"]
    return run_command(cmd, "Testes Administrativos")


def run_functional_tests() -> bool:
    """Executa testes funcionais específicos"""
    success = True
    
    # Testes de Age Groups
    cmd = ["pytest", "tests/test_age_groups.py", "-v", "--tb=short"]
    success &= run_command(cmd, "Testes de Age Groups")
    
    # Testes de Enrollments
    cmd = ["pytest", "tests/test_enrollments.py", "-v", "--tb=short"]
    success &= run_command(cmd, "Testes de Enrollments")
    
    return success


def run_integration_tests() -> bool:
    """Executa testes de integração"""
    cmd = ["pytest", "tests/test_integration.py", "-v", "--tb=short", "-m", "integration"]
    return run_command(cmd, "Testes de Integração")


def run_performance_tests() -> bool:
    """Executa testes de performance"""
    cmd = ["pytest", "tests/test_performance.py", "-v", "--tb=short"]
    return run_command(cmd, "Testes de Performance")


def run_edge_case_tests() -> bool:
    """Executa testes de casos extremos"""
    cmd = ["pytest", "tests/test_edge_cases.py", "-v", "--tb=short"]
    return run_command(cmd, "Testes de Casos Extremos")


def run_all_tests() -> bool:
    """Executa todos os testes"""
    cmd = ["pytest", "tests/", "-v", "--tb=short", "-m", "not slow"]
    return run_command(cmd, "Todos os Testes (exceto lentos)")


def run_quick_tests() -> bool:
    """Executa apenas testes rápidos"""
    success = True
    success &= run_unit_tests()
    success &= run_auth_tests()
    success &= run_admin_tests()
    success &= run_functional_tests()
    return success


def run_full_suite() -> bool:
    """Executa suíte completa de testes"""
    success = True
    
    print("🚀 Executando suíte completa de testes...")
    
    success &= run_unit_tests()
    success &= run_auth_tests()
    success &= run_admin_tests()
    success &= run_functional_tests()
    success &= run_integration_tests()
    success &= run_performance_tests()
    success &= run_edge_case_tests()
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Executa testes do sistema de enrollment")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["unit", "auth", "admin", "functional", "integration", "performance", "edge", "all", "quick", "full"],
        default="quick",
        help="Suíte de testes para executar (padrão: quick)"
    )
    parser.add_argument(
        "--no-env-check",
        action="store_true",
        help="Pula verificação do ambiente"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Executa com cobertura de código"
    )
    
    args = parser.parse_args()
    
    print("🧪 Sistema de Testes - Enrollment API")
    print("=" * 50)
    
    # Verificar ambiente
    if not args.no_env_check:
        if not check_environment():
            print("\n❌ Ambiente não está pronto. Corrija os problemas acima.")
            sys.exit(1)
    
    # Adicionar coverage se solicitado
    if args.coverage:
        print("📊 Executando com cobertura de código...")
    
    start_time = time.time()
    success = False
    
    # Executar suíte selecionada
    if args.suite == "unit":
        success = run_unit_tests()
    elif args.suite == "auth":
        success = run_auth_tests()
    elif args.suite == "admin":
        success = run_admin_tests()
    elif args.suite == "functional":
        success = run_functional_tests()
    elif args.suite == "integration":
        success = run_integration_tests()
    elif args.suite == "performance":
        success = run_performance_tests()
    elif args.suite == "edge":
        success = run_edge_case_tests()
    elif args.suite == "all":
        success = run_all_tests()
    elif args.suite == "quick":
        success = run_quick_tests()
    elif args.suite == "full":
        success = run_full_suite()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print(f"⏱️ Tempo total: {duration:.2f} segundos")
    
    if success:
        print("🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("💥 Alguns testes falharam!")
        sys.exit(1)


if __name__ == "__main__":
    main() 