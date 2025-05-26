# 🎯 Enrollment API - Sistema de Inscrições

Sistema completo de gerenciamento de inscrições com processamento assíncrono, desenvolvido com arquitetura moderna e escalável.

## 📋 Visão Geral

Este projeto implementa um **sistema de enrollment** robusto que permite:

- **Gerenciamento de grupos etários** (Age Groups) com validação
- **Processamento de inscrições** com validação de CPF
- **Processamento assíncrono** via fila de mensagens
- **Autenticação Basic Auth** com controle de acesso por roles
- **Arquitetura escalável** com Docker e microserviços

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Configuration   │    │    FAST API     │    │   Final User    │
│     User        │───▶│                 │◀───│                 │
└─────────────────┘    │  Age Groups API │    └─────────────────┘
                       │  Enrollment API │
                       └─────────┬───────┘
                                 │ Write/Read
                                 ▼
                       ┌─────────────────┐
                       │   Document DB   │
                       │   (MongoDB)     │
                       └─────────┬───────┘
                                 │ Write
                                 ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Enrollment     │    │  Enrollment     │    │  Enrollment     │
│   Processor     │◀───│     Queue       │◀───│      API        │
│ (Python Worker)│    │  (RabbitMQ)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎯 Componentes Principais

- **FastAPI** - API REST moderna com documentação automática
- **MongoDB** - Banco de dados NoSQL para persistência flexível
- **RabbitMQ** - Fila de mensagens para processamento assíncrono
- **Python Worker** - Processador standalone para enrollments
- **Basic Auth** - Sistema de autenticação simples e eficaz
- **Docker** - Containerização para portabilidade e escalabilidade

## 🚀 Funcionalidades

### 👥 Gerenciamento de Age Groups

- ✅ **Criar** grupos etários (min_age, max_age)
- ✅ **Listar** todos os grupos
- ✅ **Buscar** grupo específico
- ✅ **Atualizar** grupo existente
- ✅ **Deletar** grupo

### 📝 Sistema de Enrollment

- ✅ **Criar inscrição** com validação automática
- ✅ **Validação de CPF** obrigatória
- ✅ **Verificação de idade** contra age groups
- ✅ **Processamento assíncrono** via RabbitMQ
- ✅ **Consulta de status** em tempo real

### 🔐 Autenticação e Autorização

- ✅ **Basic Auth** implementado
- ✅ **Usuários em arquivo estático** (users.json)
- ✅ **Controle de acesso** por roles (admin/user)
- ✅ **Endpoints administrativos** protegidos

### ⚙️ Processamento Assíncrono

- ✅ **Worker Python** standalone
- ✅ **RabbitMQ** como fila de mensagens
- ✅ **Processamento com delay** configurável
- ✅ **Atualização de status** automática

## 🛠️ Tecnologias Utilizadas

| Componente    | Tecnologia | Justificativa                              |
| ------------- | ---------- | ------------------------------------------ |
| **API**       | FastAPI    | Performance e documentação automática      |
| **Database**  | MongoDB    | Flexibilidade para dados não estruturados  |
| **Queue**     | RabbitMQ   | Fila de mensagens robusta e confiável      |
| **Worker**    | Python     | Processamento assíncrono eficiente         |
| **Auth**      | Basic Auth | Simplicidade e facilidade de implementação |
| **Container** | Docker     | Portabilidade e isolamento                 |
| **Tests**     | Pytest     | Cobertura completa de testes               |

## 📁 Estrutura do Projeto

```
├── src/
│   ├── enroll_api/                 # API Principal
│   │   ├── app/
│   │   │   ├── auth/              # Sistema de autenticação
│   │   │   │   ├── __init__.py
│   │   │   │   └── basic_auth.py  # Basic Auth implementation
│   │   │   ├── config/            # Configurações
│   │   │   │   ├── config.py      # Configurações da aplicação
│   │   │   │   └── users.json     # Usuários estáticos
│   │   │   ├── db/                # Conexões de banco
│   │   │   │   ├── mongo.py       # MongoDB connection
│   │   │   │   └── rabbitMQ.py    # RabbitMQ connection
│   │   │   ├── endpoints/         # Endpoints da API
│   │   │   │   ├── admin.py       # Endpoints administrativos
│   │   │   │   ├── age_groups.py  # CRUD Age Groups
│   │   │   │   └── enrollment.py  # Enrollment endpoints
│   │   │   ├── models/            # Modelos Pydantic
│   │   │   │   ├── age_group.py   # Age Group models
│   │   │   │   └── enrollment.py  # Enrollment models
│   │   │   ├── services/          # Lógica de negócio
│   │   │   │   ├── age_groups.py  # Age Groups service
│   │   │   │   └── enrollment.py  # Enrollment service
│   │   │   └── main.py            # FastAPI app
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── worker/                     # Worker Assíncrono
│       ├── worker.py              # Processador de enrollments
│       ├── Dockerfile
│       └── requirements.txt
├── tests/                          # Testes Completos
│   ├── conftest.py                # Configurações de teste
│   ├── test_admin.py              # Testes administrativos
│   ├── test_age_groups.py         # Testes Age Groups
│   ├── test_auth.py               # Testes autenticação
│   ├── test_edge_cases.py         # Casos extremos
│   ├── test_enrollments.py        # Testes Enrollments
│   ├── test_integration.py        # Testes integração
│   ├── test_performance.py        # Testes performance
│   ├── test_unit.py               # Testes unitários
│   └── README.md                  # Documentação testes
├── docs/                           # Documentação
│   └── AUTHENTICATION.md          # Guia autenticação
├── docker-compose.yaml            # Orquestração completa
├── pytest.ini                     # Configuração testes
├── run_tests.py                   # Script de testes
└── README.md                      # Este arquivo
```

## 🔧 Configuração e Execução

### 📋 Pré-requisitos

- **Docker** e **Docker Compose**
- **Python 3.12+** (para desenvolvimento)
- **Git** para clonagem

### 🚀 Execução Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/lksmaxx/enroll_api.git
cd enroll_api

# 2. Setup automático (instala dependências + inicia Docker)
make setup

# 3. Verifique se está funcionando
curl http://localhost:8000/
```

### 🛠️ Opções de Instalação

#### Opção 1: Makefile (Linux/macOS)

```bash
# Setup completo para desenvolvimento
make dev-setup

# Apenas dependências básicas
make install

# Executar testes
make test-coverage
```

#### Opção 1b: PowerShell (Windows)

```powershell
# Instalar dependências
.\make.ps1 install

# Executar testes
.\make.ps1 test

# Executar testes com cobertura
.\make.ps1 test-coverage

# Ver todos os comandos
.\make.ps1 help
```

#### Opção 2: Requirements.txt

```bash
# Dependências básicas (inclui coverage, pytest)
pip install -r requirements.txt

# Dependências de desenvolvimento (black, flake8, mypy)
pip install -r requirements-dev.txt

# Iniciar ambiente Docker
docker compose up -d
```

#### Opção 3: Setup.py

```bash
# Instalação básica
pip install -e .

# Com dependências de desenvolvimento
pip install -e ".[dev]"

# Apenas dependências de teste
pip install -e ".[test]"
```

### 🧪 Executando Testes

#### Com Makefile (Linux/macOS)

```bash
# Testes rápidos
make test

# Testes com cobertura
make test-coverage

# Testes com relatório HTML
make test-html

# Testes por categoria
make test-unit
make test-auth
make test-admin
make test-integration
```

#### Com PowerShell (Windows)

```powershell
# Testes rápidos
.\make.ps1 test

# Testes com cobertura
.\make.ps1 test-coverage

# Testes com relatório HTML
.\make.ps1 test-html

# Iniciar/parar Docker
.\make.ps1 docker-up
.\make.ps1 docker-down
```

#### Com Script Python (Multiplataforma)

```bash
# Testes rápidos
python run_tests.py quick

# Testes completos com cobertura
python run_tests.py coverage

# Categoria específica
python run_tests.py auth
python run_tests.py admin
python run_tests.py integration
```

#### Com Pytest Direto

```bash
# Executar todos os testes
pytest tests/ -v

# Com cobertura
coverage run -m pytest tests/
coverage report --show-missing
coverage html
```

## 🔐 Autenticação

### 👤 Usuários Padrão

| Usuário    | Senha         | Role  | Descrição              |
| ---------- | ------------- | ----- | ---------------------- |
| `admin`    | `secret123`   | admin | Administrador completo |
| `manager`  | `manager789`  | admin | Gerente administrativo |
| `config`   | `config123`   | user  | Usuário configuração   |
| `operator` | `operator456` | user  | Operador sistema       |

### 🔑 Níveis de Acesso

- **🔓 Público**: Health check (`GET /`)
- **🔒 Autenticado**: Leitura de dados, criação de enrollments
- **👑 Admin**: Operações CRUD completas, endpoints administrativos

## 📚 Exemplos de Uso

### 1. 👥 Gerenciar Age Groups (Admin)

```bash
# Criar age group
curl -u admin:secret123 -X POST \
  -H "Content-Type: application/json" \
  -d '{"min_age": 18, "max_age": 25}' \
  http://localhost:8000/age-groups/

# Listar age groups
curl -u config:config123 http://localhost:8000/age-groups/
```

### 2. 📝 Criar Enrollment

```bash
# Criar enrollment
curl -u config:config123 -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "age": 22,
    "cpf": "123.456.789-01"
  }' \
  http://localhost:8000/enrollments/

# Verificar status
curl -u config:config123 \
  http://localhost:8000/enrollments/{enrollment_id}
```

### 3. 🛠️ Administração

```bash
# Listar usuários
curl -u admin:secret123 http://localhost:8000/admin/users

# Status do sistema
curl -u admin:secret123 http://localhost:8000/admin/system/auth-status

# Recarregar usuários
curl -u admin:secret123 -X POST \
  http://localhost:8000/admin/users/reload
```

## 🔄 Fluxo de Processamento

### 📊 Diagrama de Sequência

```
Configuration User    FastAPI    MongoDB    RabbitMQ    Worker
       │                │          │          │          │
       │─── POST age-group ────────▶│          │          │
       │                │──────────▶│          │          │
       │◀─── 200 OK ───────────────│          │          │
       │                │          │          │          │
Final User             │          │          │          │
       │                │          │          │          │
       │─── POST enrollment ───────▶│          │          │
       │                │──────────▶│          │          │
       │                │─────────────────────▶│          │
       │◀─── 200 OK ───────────────│          │          │
       │                │          │          │──────────▶│
       │                │          │          │          │─── process (2s+)
       │                │          │◀─────────────────────│
       │                │          │          │          │
       │─── GET status ────────────▶│          │          │
       │                │──────────▶│          │          │
       │◀─── processed ────────────│          │          │
```

### ⚙️ Etapas do Processamento

1. **Validação**: CPF e idade contra age groups
2. **Persistência**: Salva enrollment no MongoDB
3. **Enfileiramento**: Publica na fila RabbitMQ
4. **Processamento**: Worker processa com delay configurável
5. **Atualização**: Status atualizado no MongoDB

## 🧪 Testes

### 📊 Cobertura de Testes

O projeto possui uma suíte completa de **107 testes** com **83.59% de cobertura de código**:

- **✅ Testes Unitários**: Modelos e serviços isolados (14 testes)
- **✅ Testes de Autenticação**: Basic Auth e permissões (13 testes)
- **✅ Testes Administrativos**: Endpoints admin (15 testes)
- **✅ Testes de Validação**: CPF, nomes, idades (12 testes)
- **✅ Testes de Age Groups**: CRUD e validações (10 testes)
- **✅ Testes de Enrollments**: Fluxo completo (13 testes)
- **✅ Testes de Integração**: Workflows end-to-end (10 testes)
- **✅ Testes de Performance**: Carga e concorrência (6 testes)
- **✅ Testes de Casos Extremos**: Segurança e robustez (14 testes)

### 🎯 Execução de Testes

#### Testes Rápidos (Desenvolvimento)

```bash
# Testes básicos (padrão)
python run_tests.py

# Testes rápidos com cobertura
python run_tests.py quick --coverage
```

#### Testes por Categoria

```bash
python run_tests.py unit          # Testes unitários
python run_tests.py auth          # Testes autenticação
python run_tests.py admin         # Testes administrativos
python run_tests.py validation    # Testes validação
python run_tests.py functional    # Age Groups + Enrollments
python run_tests.py integration   # Testes integração
python run_tests.py performance   # Testes performance
python run_tests.py edge          # Casos extremos
```

#### Suítes Completas

```bash
python run_tests.py all           # Todos (exceto lentos)
python run_tests.py full          # Suíte completa
python run_tests.py coverage      # Suíte completa com coverage
```

### 📈 Relatórios de Cobertura

#### Cobertura no Terminal

```bash
# Testes com relatório de cobertura
python run_tests.py quick --coverage

# Relatório sem linhas não cobertas
python run_tests.py coverage --no-missing
```

#### Relatório HTML Interativo

```bash
# Gerar relatório HTML
python run_tests.py full --coverage --html

# Abrir relatório (gerado em htmlcov/index.html)
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

### 📊 Estatísticas de Cobertura

| Módulo                       | Cobertura | Status       |
| ---------------------------- | --------- | ------------ |
| **enrollment.py** (service)  | 100%      | ✅ Completo  |
| **enrollment.py** (endpoint) | 100%      | ✅ Completo  |
| **main.py**                  | 100%      | ✅ Completo  |
| **config.py**                | 95%       | ✅ Excelente |
| **admin.py**                 | 94.74%    | ✅ Excelente |
| **enrollment.py** (model)    | 92.86%    | ✅ Muito Bom |
| **validators.py**            | 90.38%    | ✅ Muito Bom |
| **age_group.py** (model)     | 87.76%    | ✅ Muito Bom |
| **mongo.py**                 | 87.10%    | ✅ Muito Bom |
| **age_groups.py** (endpoint) | 83.33%    | ✅ Bom       |
| **age_groups.py** (service)  | 80.65%    | ✅ Bom       |
| **rabbitMQ.py**              | 82.35%    | ✅ Bom       |
| **basic_auth.py**            | 64.41%    | ⚠️ Melhorar  |

### 🔧 Configuração de Testes

#### Pré-requisitos

```bash
# Instalar todas as dependências (inclui coverage)
pip install -r requirements.txt

# OU instalar dependências de desenvolvimento (opcional)
pip install -r requirements-dev.txt

# Iniciar ambiente Docker
docker compose up -d
```

#### Configuração Avançada

```bash
# Pular verificação de ambiente
python run_tests.py unit --no-env-check

# Executar com pytest diretamente
pytest tests/ -v --tb=short

# Coverage manual
coverage run --source=src/enroll_api -m pytest tests/
coverage report --show-missing
coverage html
```

## 🐳 Docker e Orquestração

### 📦 Serviços

- **enroll_api**: API FastAPI principal
- **mongo**: MongoDB para persistência
- **rabbitmq**: RabbitMQ para filas
- **worker**: Worker Python para processamento

### 🔧 Configuração

```yaml
# docker-compose.yaml
services:
  enroll_api:
    build: ./src/enroll_api
    ports: ["8000:8000"]
    environment:
      - BASIC_AUTH_USERS=admin:secret123,config:config123

  mongo:
    image: mongo:latest
    ports: ["27017:27017"]

  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]

  worker:
    build: ./src/worker
    depends_on: [mongo, rabbitmq]
```

## 📈 Monitoramento

### 🔍 Health Checks

```bash
# API Health
curl http://localhost:8000/

# RabbitMQ Management
http://localhost:15672/ (guest/guest)

# MongoDB Status
docker exec -it enroll_api_mongo mongosh
```

### 📊 Métricas

- **Status de enrollments** via API
- **Fila RabbitMQ** via management interface
- **Logs de processamento** via Docker logs

## 🔒 Segurança

### 🛡️ Medidas Implementadas

- **Basic Auth** com proteção contra timing attacks
- **Controle de acesso** baseado em roles
- **Validação de entrada** rigorosa
- **Sanitização de dados** automática
- **Headers de segurança** apropriados

### ⚠️ Recomendações para Produção

- **HTTPS obrigatório** para Basic Auth
- **Senhas criptografadas** no arquivo users.json
- **Rate limiting** para endpoints
- **Logs de auditoria** para acesso
- **Backup automático** do MongoDB

## 🚀 Próximos Passos

### 🎯 Melhorias Planejadas

- **JWT Authentication** para sessões stateless
- **OAuth 2.0** para integração externa
- **API Keys** para acesso programático
- **Criptografia de senhas** (bcrypt/argon2)
- **Audit logging** completo
- **Métricas Prometheus** para monitoramento
- **CI/CD pipeline** automatizado

### 🔧 Extensões Possíveis

- **Multi-tenancy** para diferentes organizações
- **Notificações** por email/SMS
- **Dashboard web** para administração
- **API versioning** para compatibilidade
- **Cache Redis** para performance

### 💡 Melhorias Identificadas

#### 🛡️ Validação de Age Groups

- **Proteção contra exclusão**: Impedir deletar age groups com enrollments ativos
- **Validação de atualização**: Verificar se mudanças não invalidam enrollments existentes
- **Migração automática**: Realocar enrollments quando age groups são modificados

#### ⚖️ Resolução de Colisões

- **Detecção de sobreposição**: Validar que age groups não se sobreponham
- **Estratégia de prioridade**: Definir qual age group usar quando há múltiplas opções
- **Configuração flexível**: Permitir ou bloquear sobreposições conforme regra de negócio

#### 🔄 Processamento Robusto

- **Retry automático**: Reprocessar enrollments que falharam
- **Dead letter queue**: Isolar enrollments com problemas persistentes
- **Monitoramento de fila**: Alertas para filas congestionadas

#### 📊 Observabilidade

- **Logs estruturados**: Facilitar debugging e auditoria
- **Métricas de negócio**: Acompanhar taxa de sucesso dos enrollments
- **Health checks avançados**: Verificar dependências externas

## 📞 Suporte

### 🐛 Reportar Problemas

1. **Logs da aplicação**: `docker compose logs enroll_api`
2. **Logs do worker**: `docker compose logs worker`
3. **Status dos serviços**: `docker compose ps`
4. **Testes de diagnóstico**: `python run_tests.py quick`

### 📖 Documentação

- **API Docs**: http://localhost:8000/docs (Swagger)
- **Autenticação**: [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md)
- **Testes**: [tests/README.md](tests/README.md)

## 👨‍💻 Autor

**Lucas Maximino Torres**

- 📧 Email: [lucasmaximinotorres@gmail.com](mailto:lucasmaximinotorres@gmail.com)
- 🐙 GitHub: [@lksmaxx](https://github.com/lksmaxx)
- 📂 Repositório: [enroll_api](https://github.com/lksmaxx/enroll_api)

### 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. **Fazer fork** do projeto
2. **Criar uma branch** para sua feature (`git checkout -b feature/nova-feature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/nova-feature`)
5. **Abrir um Pull Request**

### 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

**🎉 Sistema pronto para produção com arquitetura robusta e escalável!**
