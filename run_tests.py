#!/usr/bin/env python3
"""
Script para executar testes do sistema de enrollment de forma organizada.
Inclui suporte completo para cobertura de código com coverage.py
"""

import subprocess
import sys
import os
import argparse
import time
from typing import List, Optional


def run_command(cmd: List[str], description: str, capture_output: bool = True) -> bool:
    """Executa um comando e retorna True se bem-sucedido"""
    print(f"\n🔄 {description}")
    print(f"Executando: {' '.join(cmd)}")
    
    try:
        if capture_output:
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
        else:
            # Para comandos interativos como coverage report
            result = subprocess.run(cmd)
            return result.returncode == 0
            
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
    
    # Verificar se coverage está instalado
    try:
        subprocess.run(["coverage", "--version"], capture_output=True, check=True)
        print("✅ coverage instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ coverage não encontrado. Instale com: pip install coverage")
        print("   Testes continuarão sem cobertura de código")
    
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


def build_test_command(test_files: List[str], use_coverage: bool = False, extra_args: List[str] = None) -> List[str]:
    """Constrói comando de teste com ou sem coverage"""
    if extra_args is None:
        extra_args = []
    
    if use_coverage:
        cmd = ["coverage", "run", "--source=src/enroll_api", "--append", "-m", "pytest"]
    else:
        cmd = ["pytest"]
    
    cmd.extend(test_files)
    cmd.extend(["-v", "--tb=short"])
    cmd.extend(extra_args)
    
    return cmd


def run_unit_tests(use_coverage: bool = False) -> bool:
    """Executa testes unitários"""
    cmd = build_test_command(["tests/test_unit.py"], use_coverage)
    return run_command(cmd, "Testes Unitários")


def run_auth_tests(use_coverage: bool = False) -> bool:
    """Executa testes de autenticação"""
    cmd = build_test_command(["tests/test_auth.py"], use_coverage)
    return run_command(cmd, "Testes de Autenticação")


def run_admin_tests(use_coverage: bool = False) -> bool:
    """Executa testes administrativos"""
    cmd = build_test_command(["tests/test_admin.py"], use_coverage)
    return run_command(cmd, "Testes Administrativos")


def run_validation_tests(use_coverage: bool = False) -> bool:
    """Executa testes de validação"""
    cmd = build_test_command(["tests/test_validation.py"], use_coverage)
    return run_command(cmd, "Testes de Validação")


def run_functional_tests(use_coverage: bool = False) -> bool:
    """Executa testes funcionais específicos"""
    success = True
    
    # Testes de Age Groups
    cmd = build_test_command(["tests/test_age_groups.py"], use_coverage)
    success &= run_command(cmd, "Testes de Age Groups")
    
    # Testes de Enrollments
    cmd = build_test_command(["tests/test_enrollments.py"], use_coverage)
    success &= run_command(cmd, "Testes de Enrollments")
    
    return success


def run_integration_tests(use_coverage: bool = False) -> bool:
    """Executa testes de integração"""
    cmd = build_test_command(["tests/test_integration.py"], use_coverage, ["-m", "integration"])
    return run_command(cmd, "Testes de Integração")


def run_performance_tests(use_coverage: bool = False) -> bool:
    """Executa testes de performance"""
    cmd = build_test_command(["tests/test_performance.py"], use_coverage)
    return run_command(cmd, "Testes de Performance")


def run_edge_case_tests(use_coverage: bool = False) -> bool:
    """Executa testes de casos extremos"""
    cmd = build_test_command(["tests/test_edge_cases.py"], use_coverage)
    return run_command(cmd, "Testes de Casos Extremos")


def run_all_tests(use_coverage: bool = False) -> bool:
    """Executa todos os testes"""
    cmd = build_test_command(["tests/"], use_coverage, ["-m", "not slow"])
    return run_command(cmd, "Todos os Testes (exceto lentos)")


def run_quick_tests(use_coverage: bool = False) -> bool:
    """Executa apenas testes rápidos"""
    success = True
    success &= run_unit_tests(use_coverage)
    success &= run_auth_tests(use_coverage)
    success &= run_admin_tests(use_coverage)
    success &= run_validation_tests(use_coverage)
    success &= run_functional_tests(use_coverage)
    return success


def run_full_suite(use_coverage: bool = False) -> bool:
    """Executa suíte completa de testes"""
    success = True
    
    print("🚀 Executando suíte completa de testes...")
    
    success &= run_unit_tests(use_coverage)
    success &= run_auth_tests(use_coverage)
    success &= run_admin_tests(use_coverage)
    success &= run_validation_tests(use_coverage)
    success &= run_functional_tests(use_coverage)
    success &= run_integration_tests(use_coverage)
    success &= run_performance_tests(use_coverage)
    success &= run_edge_case_tests(use_coverage)
    
    return success


def clear_coverage_data():
    """Limpa dados de cobertura anteriores"""
    try:
        if os.path.exists(".coverage"):
            os.remove(".coverage")
        print("🧹 Dados de cobertura anteriores limpos")
    except Exception as e:
        print(f"⚠️ Erro ao limpar dados de cobertura: {e}")


def generate_coverage_report(html: bool = False, show_missing: bool = True):
    """Gera relatório de cobertura"""
    print("\n📊 Gerando relatório de cobertura...")
    
    # Relatório no terminal
    cmd = ["coverage", "report"]
    if show_missing:
        cmd.append("--show-missing")
    
    success = run_command(cmd, "Relatório de Cobertura", capture_output=False)
    
    if html and success:
        # Relatório HTML
        cmd_html = ["coverage", "html", "--directory=htmlcov"]
        if run_command(cmd_html, "Relatório HTML de Cobertura"):
            print("📄 Relatório HTML gerado em: htmlcov/index.html")
            print("   Abra o arquivo no navegador para visualizar")
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Executa testes do sistema de enrollment")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["unit", "auth", "admin", "validation", "functional", "integration", "performance", "edge", "all", "quick", "full", "coverage"],
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
    parser.add_argument(
        "--html",
        action="store_true",
        help="Gera relatório HTML de cobertura (requer --coverage)"
    )
    parser.add_argument(
        "--no-missing",
        action="store_true",
        help="Não mostra linhas não cobertas no relatório"
    )
    
    args = parser.parse_args()
    
    print("🧪 Sistema de Testes - Enrollment API")
    print("=" * 50)
    
    # Verificar ambiente
    if not args.no_env_check:
        if not check_environment():
            print("\n❌ Ambiente não está pronto. Corrija os problemas acima.")
            sys.exit(1)
    
    # Configurar coverage
    use_coverage = args.coverage or args.suite == "coverage"
    if use_coverage:
        print("📊 Executando com cobertura de código...")
        clear_coverage_data()
    
    start_time = time.time()
    success = False
    
    # Executar suíte selecionada
    if args.suite == "unit":
        success = run_unit_tests(use_coverage)
    elif args.suite == "auth":
        success = run_auth_tests(use_coverage)
    elif args.suite == "admin":
        success = run_admin_tests(use_coverage)
    elif args.suite == "validation":
        success = run_validation_tests(use_coverage)
    elif args.suite == "functional":
        success = run_functional_tests(use_coverage)
    elif args.suite == "integration":
        success = run_integration_tests(use_coverage)
    elif args.suite == "performance":
        success = run_performance_tests(use_coverage)
    elif args.suite == "edge":
        success = run_edge_case_tests(use_coverage)
    elif args.suite == "all":
        success = run_all_tests(use_coverage)
    elif args.suite == "quick":
        success = run_quick_tests(use_coverage)
    elif args.suite == "full" or args.suite == "coverage":
        success = run_full_suite(use_coverage)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Gerar relatório de cobertura se solicitado
    if use_coverage and success:
        generate_coverage_report(html=args.html, show_missing=not args.no_missing)
    
    print("\n" + "=" * 50)
    print(f"⏱️ Tempo total: {duration:.2f} segundos")
    
    if success:
        print("🎉 Todos os testes passaram!")
        if use_coverage:
            print("📊 Relatório de cobertura gerado acima")
            if args.html:
                print("📄 Relatório HTML disponível em htmlcov/index.html")
        sys.exit(0)
    else:
        print("💥 Alguns testes falharam!")
        sys.exit(1)


if __name__ == "__main__":
    main() 