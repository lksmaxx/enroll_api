# PowerShell script para Enrollment API
param([string]$Command = "help")

switch ($Command.ToLower()) {
    "help" {
        Write-Host "Comandos disponiveis:" -ForegroundColor Cyan
        Write-Host "  help                 Mostra esta ajuda" -ForegroundColor Green
        Write-Host "  install              Instala dependencias basicas" -ForegroundColor Green
        Write-Host "  test                 Executa testes rapidos" -ForegroundColor Green
        Write-Host "  test-coverage        Executa testes com cobertura" -ForegroundColor Green
        Write-Host "  test-html            Executa testes com HTML" -ForegroundColor Green
        Write-Host "  docker-up            Inicia ambiente Docker" -ForegroundColor Green
        Write-Host "  docker-down          Para ambiente Docker" -ForegroundColor Green
        Write-Host "  status               Mostra status dos servicos" -ForegroundColor Green
    }
    "install" {
        Write-Host "Instalando dependencias..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
    "test" {
        Write-Host "Executando testes rapidos..." -ForegroundColor Yellow
        python run_tests.py quick
    }
    "test-coverage" {
        Write-Host "Executando testes com cobertura..." -ForegroundColor Yellow
        python run_tests.py coverage
    }
    "test-html" {
        Write-Host "Executando testes com HTML..." -ForegroundColor Yellow
        python run_tests.py coverage --html
    }
    "docker-up" {
        Write-Host "Iniciando Docker..." -ForegroundColor Yellow
        docker compose up -d
    }
    "docker-down" {
        Write-Host "Parando Docker..." -ForegroundColor Yellow
        docker compose down
    }
    "status" {
        Write-Host "Status dos servicos:" -ForegroundColor Yellow
        docker compose ps
    }
    default {
        Write-Host "Comando desconhecido: $Command" -ForegroundColor Red
        Write-Host "Execute .\make.ps1 help para ver comandos" -ForegroundColor Yellow
    }
} 