# Testes do Sistema de Enrollment

Este diretório contém uma suíte completa de testes para o sistema de enrollment, organizada em diferentes categorias para garantir cobertura abrangente e qualidade do código.

## Estrutura dos Testes

### 📁 Organização dos Arquivos

```
tests/
├── conftest.py              # Configurações e fixtures compartilhadas
├── test_unit.py             # Testes unitários (componentes isolados)
├── test_auth.py             # Testes de autenticação e autorização
├── test_admin.py            # Testes de endpoints administrativos
├── test_validation.py       # Testes de validação de dados
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

#### 2. **Testes de Autenticação** (`test_auth.py`)

- Basic Auth implementation
- Controle de acesso por roles
- Proteção de endpoints
- Headers malformados

#### 3. **Testes Administrativos** (`test_admin.py`)

- Endpoints de administração
- Gerenciamento de usuários
- Permissões específicas
- Operações privilegiadas

#### 4. **Testes de Validação** (`test_validation.py`)

- Validação de CPF matemática
- Validação de nomes e idades
- JSON malformado
- Tipos de dados incorretos

#### 5. **Testes Específicos de Funcionalidade**

- **Age Groups** (`test_age_groups.py`): CRUD completo, validações
- **Enrollments** (`test_enrollments.py`): Criação, processamento, status

#### 6. **Testes de Integração** (`test_integration.py`)

- Testam fluxo completo da aplicação
- Verificam integração entre API, banco e worker
- Workflows end-to-end

#### 7. **Testes de Performance** (`test_performance.py`)

- Testes de carga e concorrência
- Medição de tempos de resposta
- Verificação de estabilidade sob stress

#### 8. **Testes de Casos Extremos** (`test_edge_cases.py`)

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
   pip install pytest requests pymongo pika coverage
   ```

### 🎯 Script de Testes Integrado

O projeto inclui um script completo para execução de testes com suporte a cobertura de código:

```bash
# Executar testes rápidos (padrão)
python run_tests.py

# Executar testes específicos
python run_tests.py unit           # Apenas unitários
python run_tests.py auth           # Apenas autenticação
python run_tests.py admin          # Apenas administrativos
python run_tests.py validation     # Apenas validação
python run_tests.py functional     # Age Groups + Enrollments
python run_tests.py integration    # Integração completa
python run_tests.py performance    # Performance e carga
python run_tests.py edge           # Casos extremos

# Executar suítes completas
python run_tests.py all            # Todos (exceto lentos)
python run_tests.py full           # Suíte completa
python run_tests.py quick          # Testes rápidos
```

### 📊 Cobertura de Código

#### Executar com Coverage

```bash
# Testes rápidos com cobertura
python run_tests.py quick --coverage

# Suíte completa com cobertura
python run_tests.py coverage

# Com relatório HTML
python run_tests.py full --coverage --html

# Apenas cobertura (sem mostrar linhas não cobertas)
python run_tests.py coverage --no-missing
```

#### Relatórios de Coverage

O sistema gera automaticamente:

1. **Relatório no Terminal**: Mostra percentual de cobertura por arquivo
2. **Relatório HTML**: Arquivo interativo em `htmlcov/index.html`
3. **Arquivo XML**: Para integração com CI/CD em `coverage.xml`

#### Configuração de Coverage

O arquivo `.coveragerc` configura:

- **Source**: `src/enroll_api` (código da aplicação)
- **Omit**: Exclui testes, cache, venv
- **Exclude**: Ignora linhas de debug, abstracts, etc.
- **Precision**: 2 casas decimais

### 🔧 Comandos Pytest Diretos

#### Executar todos os testes:

```bash
pytest tests/
```

#### Executar testes específicos:

```bash
# Apenas testes unitários
pytest tests/test_unit.py

# Apenas testes de autenticação
pytest tests/test_auth.py

# Apenas testes de age groups
pytest tests/test_age_groups.py
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

#### Executar com coverage manual:

```bash
# Com coverage básico
coverage run -m pytest tests/
coverage report

# Com coverage e HTML
coverage run --source=src/enroll_api -m pytest tests/
coverage html
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

### Estatísticas Atuais

- **95+ testes** implementados
- **8 categorias** de teste
- **78% cobertura** de código (518 linhas cobertas)
- **100% dos endpoints** funcionais testados

### Funcionalidades Testadas

#### ✅ Age Groups

- [x] Criação, leitura, atualização, exclusão
- [x] Validação de dados
- [x] Casos extremos (idades negativas, ranges inválidos)
- [x] Controle de acesso (admin vs user)

#### ✅ Enrollments

- [x] Criação e validação
- [x] Processamento assíncrono
- [x] Verificação de status
- [x] Validação de CPF matemática
- [x] Integração com age groups

#### ✅ Autenticação

- [x] Basic Auth implementation
- [x] Múltiplos usuários e roles
- [x] Proteção de endpoints
- [x] Headers malformados
- [x] Tentativas de acesso não autorizado

#### ✅ Validação

- [x] CPF com algoritmo matemático
- [x] Nomes com regras de negócio
- [x] Idades com limites
- [x] JSON malformado
- [x] Tipos de dados incorretos

#### ✅ Segurança

- [x] Tentativas de SQL/NoSQL injection
- [x] Payloads extremamente grandes
- [x] Caracteres Unicode e especiais
- [x] Valores nulos e negativos

#### ✅ Performance

- [x] Enrollments simultâneos
- [x] CRUD em massa
- [x] Tempos de resposta
- [x] Consistência sob carga

### Módulos com Melhor Cobertura

| Módulo                  | Cobertura | Status       |
| ----------------------- | --------- | ------------ |
| main.py                 | 100%      | ✅ Completo  |
| enrollment.py (service) | 100%      | ✅ Completo  |
| config.py               | 95%       | ✅ Excelente |
| admin.py                | 95%       | ✅ Excelente |
| validators.py           | 90%       | ✅ Muito Bom |

### Áreas para Melhoria

| Módulo                   | Cobertura | Prioridade |
| ------------------------ | --------- | ---------- |
| rabbitMQ.py              | 50%       | 🔴 Alta    |
| basic_auth.py            | 64%       | 🟡 Média   |
| age_groups.py (endpoint) | 70%       | 🟡 Média   |

## 🎯 Boas Práticas

### Isolamento de Testes

- Use `clean_database` para testes que modificam dados
- Testes unitários devem usar mocks
- Evite dependências entre testes

### Performance

- Marque testes lentos com `@pytest.mark.slow`
- Use `run_tests.py quick` para desenvolvimento
- Execute suíte completa antes de commits

### Cobertura

- Mantenha cobertura acima de 75%
- Foque em testar lógica de negócio crítica
- Use `--coverage --html` para análise detalhada

### Debugging

```bash
# Parar no primeiro erro
python run_tests.py unit -x

# Executar teste específico
pytest tests/test_unit.py::test_specific_function -v -s

# Ver logs detalhados
pytest tests/ -v -s --tb=long
```

## 🚀 Integração Contínua

### Comandos para CI/CD

```bash
# Verificação rápida (para PRs)
python run_tests.py quick --coverage

# Verificação completa (para main branch)
python run_tests.py full --coverage --html

# Apenas verificar se ambiente está OK
python run_tests.py unit --no-env-check
```

### Arquivos Gerados

- `.coverage`: Dados de cobertura
- `htmlcov/`: Relatório HTML interativo
- `coverage.xml`: Para ferramentas de CI/CD

## 📝 Contribuindo

### Adicionando Novos Testes

1. **Escolha a categoria** apropriada
2. **Use fixtures** existentes quando possível
3. **Adicione markers** para testes lentos
4. **Documente** casos de teste complexos
5. **Verifique cobertura** com `--coverage`

### Estrutura de Teste

```python
def test_feature_description(api_client, clean_database):
    """Descrição clara do que está sendo testado"""
    # Arrange
    setup_data = {...}

    # Act
    response = api_client.post("/endpoint", json=setup_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == expected_value
```

### Checklist para Novos Testes

- [ ] Teste passa individualmente
- [ ] Teste passa em suíte completa
- [ ] Cobertura não diminuiu
- [ ] Documentação atualizada
- [ ] Markers apropriados adicionados
