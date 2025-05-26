# Makefile para Enrollment API

.PHONY: help install install-dev test test-quick test-coverage test-html clean docker-up docker-down docker-logs

# Variáveis
PYTHON := python
PIP := pip
DOCKER_COMPOSE := docker compose

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências básicas
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento
	$(PIP) install -r requirements-dev.txt

install-editable: ## Instala o projeto em modo editável
	$(PIP) install -e .

install-all: install install-dev ## Instala todas as dependências

test: ## Executa testes rápidos
	$(PYTHON) run_tests.py quick

test-quick: ## Executa testes rápidos (alias)
	$(PYTHON) run_tests.py quick

test-coverage: ## Executa testes com cobertura
	$(PYTHON) run_tests.py coverage

test-html: ## Executa testes com cobertura e gera HTML
	$(PYTHON) run_tests.py coverage --html

test-unit: ## Executa apenas testes unitários
	$(PYTHON) run_tests.py unit

test-auth: ## Executa apenas testes de autenticação
	$(PYTHON) run_tests.py auth

test-admin: ## Executa apenas testes administrativos
	$(PYTHON) run_tests.py admin

test-integration: ## Executa apenas testes de integração
	$(PYTHON) run_tests.py integration

test-performance: ## Executa apenas testes de performance
	$(PYTHON) run_tests.py performance

test-all: ## Executa todos os testes
	$(PYTHON) run_tests.py full

docker-up: ## Inicia ambiente Docker
	$(DOCKER_COMPOSE) up -d

docker-down: ## Para ambiente Docker
	$(DOCKER_COMPOSE) down

docker-logs: ## Mostra logs do Docker
	$(DOCKER_COMPOSE) logs -f

docker-restart: ## Reinicia ambiente Docker
	$(DOCKER_COMPOSE) restart

docker-clean: ## Remove containers e volumes Docker
	$(DOCKER_COMPOSE) down -v --remove-orphans

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ dist/ build/

format: ## Formata código com black
	black src/ tests/

lint: ## Executa linting com flake8
	flake8 src/ tests/

type-check: ## Executa verificação de tipos com mypy
	mypy src/

quality: format lint type-check ## Executa todas as verificações de qualidade

setup: install docker-up ## Setup completo do projeto
	@echo "✅ Projeto configurado! Execute 'make test' para verificar."

dev-setup: install-all docker-up ## Setup completo para desenvolvimento
	@echo "✅ Ambiente de desenvolvimento configurado!"

check: test-coverage quality ## Verificação completa (testes + qualidade)

# Comandos de desenvolvimento
dev-test: ## Executa testes em modo de desenvolvimento (watch)
	$(PYTHON) -m pytest tests/ -v --tb=short -f

dev-api: ## Inicia API em modo de desenvolvimento
	cd src/enroll_api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Comandos de produção
build: ## Constrói imagens Docker
	$(DOCKER_COMPOSE) build

deploy: build docker-up ## Deploy completo
	@echo "✅ Deploy realizado!"

# Comandos de documentação
docs-serve: ## Serve documentação localmente
	mkdocs serve

docs-build: ## Constrói documentação
	mkdocs build

# Comandos de backup
backup-db: ## Backup do MongoDB
	docker exec enroll_api_mongo mongodump --out /tmp/backup
	docker cp enroll_api_mongo:/tmp/backup ./backup_$(shell date +%Y%m%d_%H%M%S)

# Comandos de monitoramento
status: ## Mostra status dos serviços
	$(DOCKER_COMPOSE) ps
	@echo "\n📊 Status da API:"
	@curl -s http://localhost:8000/ | jq . || echo "API não acessível"

logs-api: ## Mostra logs da API
	$(DOCKER_COMPOSE) logs -f enroll_api

logs-worker: ## Mostra logs do worker
	$(DOCKER_COMPOSE) logs -f worker

logs-mongo: ## Mostra logs do MongoDB
	$(DOCKER_COMPOSE) logs -f mongo

logs-rabbitmq: ## Mostra logs do RabbitMQ
	$(DOCKER_COMPOSE) logs -f rabbitmq 