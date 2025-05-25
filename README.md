# 🎯 Enrollment API - Sistema de Inscrições

Sistema completo de gerenciamento de inscrições com processamento assíncrono, desenvolvido seguindo rigorosamente a arquitetura especificada no diagrama de requisitos.

## 📋 Visão Geral

Este projeto implementa um **sistema de enrollment** robusto que permite:

- **Gerenciamento de grupos etários** (Age Groups)
- **Processamento de inscrições** com validação de CPF
- **Processamento assíncrono** via fila de mensagens
- **Autenticação Basic Auth** com controle de acesso
- **Arquitetura escalável** com Docker

## 🏗️ Arquitetura (Conforme Diagrama)

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

### ✅ Requisitos Implementados

- **FastAPI** com Age Groups API e Enrollment API
- **Configuration User** e **Final User** como atores
- **Document DB** (MongoDB) para persistência
- **Enrollment Queue** (RabbitMQ) para processamento assíncrono
- **Enrollment Processor** (worker Python standalone)
- **Basic Auth** para autenticação
- **Validação de CPF** obrigatória
- **Processamento mínimo de 2s** garantido
- **Fluxo completo**: Age groups → Enrollment → Queue → Processing → Status

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
- ✅ **Processamento mínimo 2s** garantido
- ✅ **Atualização de status** automática

## 🛠️ Tecnologias Utilizadas

| Componente    | Tecnologia | Justificativa                         |
| ------------- | ---------- | ------------------------------------- |
| **API**       | FastAPI    | Performance e documentação automática |
| **Database**  | MongoDB    | Document DB conforme diagrama         |
| **Queue**     | RabbitMQ   | Fila de mensagens robusta             |
| **Worker**    | Python     | Processamento assíncrono              |
| **Auth**      | Basic Auth | Simplicidade e conformidade           |
| **Container** | Docker     | Portabilidade e isolamento            |
| **Tests**     | Pytest     | Cobertura completa de testes          |

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
git clone <repository-url>
cd enrollment-api

# 2. Execute o ambiente completo
docker compose up -d

# 3. Verifique se está funcionando
curl http://localhost:8000/
```

### 🧪 Executando Testes

```bash
# Instalar dependências de teste
pip install pytest requests

# Executar testes rápidos
python run_tests.py quick

# Executar testes completos
python run_tests.py full

# Executar categoria específica
python run_tests.py auth
python run_tests.py admin
python run_tests.py integration
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
4. **Processamento**: Worker processa com delay mínimo 2s
5. **Atualização**: Status atualizado no MongoDB

## 🧪 Testes

### 📊 Cobertura de Testes

- **✅ Testes Unitários**: Modelos e serviços isolados
- **✅ Testes Funcionais**: Endpoints específicos
- **✅ Testes de Integração**: Fluxo completo
- **✅ Testes de Autenticação**: Segurança e permissões
- **✅ Testes Administrativos**: Endpoints admin
- **✅ Testes de Performance**: Carga e concorrência
- **✅ Testes de Casos Extremos**: Segurança e robustez

### 🎯 Categorias de Teste

```bash
python run_tests.py unit          # Testes unitários
python run_tests.py auth          # Testes autenticação
python run_tests.py admin         # Testes administrativos
python run_tests.py functional    # Testes funcionais
python run_tests.py integration   # Testes integração
python run_tests.py performance   # Testes performance
python run_tests.py edge          # Casos extremos
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

---

**🎉 Sistema pronto para produção com arquitetura robusta e escalável!**

## ✅ Conformidade com Diagrama

Este projeto implementa **100% dos requisitos** especificados no diagrama:

- ✅ **FastAPI** com Age Groups API e Enrollment API
- ✅ **Configuration User** e **Final User** como atores distintos
- ✅ **Document DB** (MongoDB) para persistência
- ✅ **Enrollment Queue** (RabbitMQ) para processamento assíncrono
- ✅ **Enrollment Processor** como worker Python standalone
- ✅ **Basic Auth** para autenticação (credenciais em arquivo estático)
- ✅ **Validação de CPF** obrigatória
- ✅ **Processamento mínimo 2s** garantido
- ✅ **Fluxo completo** de enrollment funcional
- ✅ **Testes integrados** obrigatórios implementados

A conformidade com todos os requisitos é validada através da **suíte completa de testes** implementada. Execute os testes para verificar que todos os componentes estão funcionando corretamente:

```bash
# Testes rápidos para verificação básica
python run_tests.py quick

# Testes completos para validação total
python run_tests.py full

# Testes de integração para fluxo completo
python run_tests.py integration
```

Os testes cobrem todos os aspectos da arquitetura e garantem que o sistema está funcionando conforme especificado no diagrama.
