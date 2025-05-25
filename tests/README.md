# Testes do Sistema de Enrollment

Este diretório contém uma suíte completa de testes para o sistema de enrollment, organizada em diferentes categorias para garantir cobertura abrangente e qualidade do código.

## Estrutura dos Testes

### 📁 Organização dos Arquivos

```
tests/
├── conftest.py              # Configurações e fixtures compartilhadas
├── test_unit.py             # Testes unitários (componentes isolados)
├── test_age_groups.py       # Testes específicos para Age Groups
├── test_enrollments.py      # Testes específicos para Enrollments
├── test_integration.py      # Testes de integração (fluxo completo)
├── test_performance.py      # Testes de performance e carga
├── test_edge_cases.py       # Testes de casos extremos
└── README.md               # Este arquivo
```

### 🧪 Tipos de Teste

#### 1. **Testes Unitários** (`test_unit.py`)

- Testam componentes isolados usando mocks
- Validam modelos Pydantic
- Testam serviços sem dependências externas
- Execução rápida e independente

#### 2. **Testes de Integração** (`test_integration.py`)

- Testam fluxo completo da aplicação
- Verificam integração entre API, banco e worker
- Requerem ambiente completo rodando

#### 3. **Testes Específicos de Funcionalidade**

- **Age Groups** (`test_age_groups.py`): CRUD completo, validações
- **Enrollments** (`test_enrollments.py`): Criação, processamento, status

#### 4. **Testes de Performance** (`test_performance.py`)

- Testes de carga e concorrência
- Medição de tempos de resposta
- Verificação de estabilidade sob stress

#### 5. **Testes de Casos Extremos** (`test_edge_cases.py`)

- Payloads malformados
- Tentativas de injection
- Valores extremos e caracteres especiais

## 🚀 Como Executar os Testes

### Pré-requisitos

1. **Ambiente rodando**:

   ```bash
   docker compose up -d
   ```

2. **Dependências instaladas**:
   ```bash
   pip install pytest requests pymongo pika
   ```

### Comandos de Execução

#### Executar todos os testes:

```bash
pytest tests/
```

#### Executar testes específicos:

```bash
# Apenas testes unitários
pytest tests/test_unit.py

# Apenas testes de age groups
pytest tests/test_age_groups.py

# Apenas testes de enrollments
pytest tests/test_enrollments.py
```

#### Executar por categoria:

```bash
# Testes rápidos (unitários)
pytest tests/test_unit.py -v

# Testes de integração
pytest tests/test_integration.py -v

# Testes de performance (podem demorar)
pytest tests/test_performance.py -v

# Excluir testes lentos
pytest tests/ -m "not slow"
```

#### Executar com mais detalhes:

```bash
# Verbose com detalhes de falhas
pytest tests/ -v -s

# Com coverage
pytest tests/ --cov=src/enroll_api

# Parar no primeiro erro
pytest tests/ -x
```

## 🔧 Configuração dos Testes

### Fixtures Principais

- **`api_client`**: Cliente HTTP para testar a API
- **`mongo_client`**: Cliente MongoDB para verificações diretas
- **`clean_database`**: Limpa o banco e fila RabbitMQ antes/depois de cada teste
- **`sample_age_groups`**: Cria age groups de exemplo
- **`valid_enrollment_data`**: Dados válidos para enrollment

### Utilitários de Limpeza

#### Função `clean_db()`

A função `clean_db()` está disponível em `tests/conftest.py` e pode ser usada para limpar completamente o sistema:

```python
from tests.conftest import clean_db

# Limpa MongoDB e RabbitMQ
clean_db()
```

#### Script de Limpeza

Para limpar o sistema via linha de comando:

```bash
# Limpa completamente o sistema
python clean_system.py
```

Este script:

- Remove todos os enrollments e age groups do MongoDB
- Purga todas as mensagens da fila RabbitMQ
- Evita que o worker processe mensagens órfãs de testes antigos

#### Fixture `clean_database`

A fixture `clean_database` é executada automaticamente em testes que a usam:

```python
def test_something(api_client, clean_database):
    # Banco e fila estão limpos antes do teste
    # ... código do teste ...
    # Banco e fila são limpos após o teste
```

**Importante**: Use `clean_database` em testes que criam dados no MongoDB ou RabbitMQ para garantir isolamento.

### Variáveis de Ambiente

```bash
# URL da API (padrão: http://localhost:8000)
export API_BASE_URL=http://localhost:8000

# MongoDB (padrão: mongodb://admin:admin@localhost:27017/)
export MONGO_URI=mongodb://admin:admin@localhost:27017/
export MONGO_DB=enroll_api_test
```

## 📊 Cobertura de Testes

### Funcionalidades Testadas

#### ✅ Age Groups

- [x] Criação, leitura, atualização, exclusão
- [x] Validação de dados
- [x] Casos extremos (idades negativas, ranges inválidos)
- [x] Sobreposição de ranges

#### ✅ Enrollments

- [x] Criação e validação
- [x] Processamento assíncrono
- [x] Verificação de status
- [x] Validação de CPF
- [x] Integração com age groups

#### ✅ Performance

- [x] Criação simultânea de enrollments
- [x] Operações CRUD em massa
- [x] Tempos de resposta
- [x] Consistência sob carga

#### ✅ Segurança

- [x] Tentativas de SQL/NoSQL injection
- [x] Payloads malformados
- [x] Caracteres especiais e Unicode

## 🎯 Boas Práticas Implementadas

### 1. **Isolamento de Testes**

- Cada teste limpa o banco antes/depois
- Uso de fixtures para setup/teardown
- Testes independentes entre si

### 2. **Mocking Adequado**

- Testes unitários usam mocks para dependências
- Testes de integração usam ambiente real
- Separação clara entre tipos de teste

### 3. **Assertions Robustas**

- Verificação de status codes
- Validação de estrutura de dados
- Verificação de efeitos colaterais

### 4. **Organização Clara**

- Classes agrupam testes relacionados
- Nomes descritivos para testes
- Documentação em docstrings

### 5. **Configuração Flexível**

- Variáveis de ambiente para configuração
- Marcadores para categorizar testes
- Opções para execução seletiva

## 🐛 Debugging de Testes

### Logs Detalhados

```bash
# Executar com logs
pytest tests/ -v -s --log-cli-level=DEBUG
```

### Executar Teste Específico

```bash
# Executar apenas um teste
pytest tests/test_enrollments.py::TestEnrollments::test_create_enrollment_success -v
```

### Verificar Ambiente

```bash
# Verificar se API está rodando
curl http://localhost:8000/

# Verificar MongoDB
docker exec -it enroll_api_mongo mongosh -u admin -p admin
```

## 📈 Métricas de Qualidade

### Objetivos de Cobertura

- **Cobertura de código**: > 90%
- **Cobertura de funcionalidades**: 100%
- **Testes de casos extremos**: Abrangente

### Critérios de Sucesso

- Todos os testes passam consistentemente
- Tempo de execução razoável (< 5 minutos)
- Detecção de regressões
- Validação de requisitos de negócio

## 🔄 Integração Contínua

### Pipeline Sugerido

1. **Testes Unitários**: Execução rápida em cada commit
2. **Testes de Integração**: Execução em PRs
3. **Testes de Performance**: Execução noturna
4. **Testes Completos**: Execução antes de releases

### Comandos para CI/CD

```bash
# Testes rápidos (CI)
pytest tests/test_unit.py tests/test_age_groups.py tests/test_enrollments.py

# Testes completos (CD)
pytest tests/ -m "not slow"

# Testes de performance (opcional)
pytest tests/test_performance.py -m "slow"
```
