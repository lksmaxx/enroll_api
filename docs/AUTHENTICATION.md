# Autenticação Basic Auth - Enrollment API

Este documento descreve como a autenticação Basic Auth foi implementada na Enrollment API.

## 📋 Visão Geral

A API utiliza **HTTP Basic Authentication** para proteger todos os endpoints, exceto o health check (`/`). A autenticação é baseada em usuário/senha carregados de um **arquivo JSON estático** e suporta diferentes níveis de acesso.

## 🔐 Configuração

### Arquivo de Usuários

Os usuários são carregados do arquivo `src/enroll_api/app/config/users.json`:

```json
{
  "users": [
    {
      "username": "admin",
      "password": "secret123",
      "role": "admin",
      "description": "Usuário administrador com acesso total"
    },
    {
      "username": "config",
      "password": "config123",
      "role": "user",
      "description": "Usuário de configuração com acesso de leitura"
    },
    {
      "username": "operator",
      "password": "operator456",
      "role": "user",
      "description": "Usuário operador com acesso de leitura"
    },
    {
      "username": "manager",
      "password": "manager789",
      "role": "admin",
      "description": "Usuário gerente com acesso administrativo"
    }
  ],
  "metadata": {
    "version": "1.0",
    "last_updated": "2024-01-01",
    "description": "Arquivo de configuração de usuários para autenticação Basic Auth"
  }
}
```

### Variáveis de Ambiente (Fallback)

```bash
# Caminho para o arquivo de usuários
USERS_FILE_PATH=app/config/users.json

# Fallback para variáveis de ambiente (caso o arquivo não exista)
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=secret123
BASIC_AUTH_USERS=admin:secret123,config:config123
```

### Usuários Padrão

| Usuário    | Senha         | Papel         | Permissões         |
| ---------- | ------------- | ------------- | ------------------ |
| `admin`    | `secret123`   | Administrador | Todas as operações |
| `manager`  | `manager789`  | Administrador | Todas as operações |
| `config`   | `config123`   | Usuário       | Leitura apenas     |
| `operator` | `operator456` | Usuário       | Leitura apenas     |

## 🛡️ Níveis de Acesso

### 🔓 **Público** (sem autenticação)

- `GET /` - Health check

### 🔒 **Autenticado** (qualquer usuário válido)

- `GET /me` - Informações do usuário
- `GET /age-groups/` - Listar age groups
- `GET /age-groups/{id}` - Buscar age group
- `POST /enrollments/` - Criar enrollment
- `GET /enrollments/{id}` - Buscar status de enrollment

### 👑 **Administrativo** (apenas usuários admin)

- `POST /age-groups/` - Criar age group
- `PUT /age-groups/{id}` - Atualizar age group
- `DELETE /age-groups/{id}` - Deletar age group
- `GET /admin/users` - Listar usuários
- `GET /admin/users/info` - Informações detalhadas dos usuários
- `POST /admin/users/reload` - Recarregar usuários do arquivo
- `GET /admin/system/auth-status` - Status do sistema de autenticação

## 🔧 Como Usar

### 1. **Curl**

```bash
# Com usuário admin
curl -u admin:secret123 http://localhost:8000/me

# Com usuário manager
curl -u manager:manager789 http://localhost:8000/admin/users

# Com usuário comum
curl -u config:config123 http://localhost:8000/age-groups/

# Criar age group (requer admin)
curl -u admin:secret123 -X POST \
  -H "Content-Type: application/json" \
  -d '{"min_age": 18, "max_age": 25}' \
  http://localhost:8000/age-groups/
```

### 2. **Endpoints Administrativos**

```bash
# Listar usuários
curl -u admin:secret123 http://localhost:8000/admin/users

# Informações detalhadas
curl -u admin:secret123 http://localhost:8000/admin/users/info

# Recarregar usuários do arquivo
curl -u admin:secret123 -X POST http://localhost:8000/admin/users/reload

# Status do sistema de autenticação
curl -u admin:secret123 http://localhost:8000/admin/system/auth-status
```

### 3. **Python Requests**

```python
import requests

# Autenticação básica
response = requests.get(
    "http://localhost:8000/admin/users",
    auth=("admin", "secret123")
)

# Verificar usuários carregados
users = response.json()
for user in users:
    print(f"{user['username']} ({user['role']}): {user['description']}")
```

## 🧪 Testando Autenticação

### Testes Automatizados

```bash
# Executar apenas testes de autenticação
python run_tests.py auth

# Executar testes administrativos
python run_tests.py admin

# Executar testes com autenticação incluída
python run_tests.py quick
```

### Testes Manuais

#### ✅ **Cenários de Sucesso**

```bash
# Health check (público)
curl http://localhost:8000/

# Login como admin
curl -u admin:secret123 http://localhost:8000/me

# Login como manager
curl -u manager:manager789 http://localhost:8000/me

# Login como usuário comum
curl -u config:config123 http://localhost:8000/me

# Admin pode criar age group
curl -u admin:secret123 -X POST \
  -H "Content-Type: application/json" \
  -d '{"min_age": 18, "max_age": 25}' \
  http://localhost:8000/age-groups/

# Manager pode listar usuários
curl -u manager:manager789 http://localhost:8000/admin/users
```

#### ❌ **Cenários de Erro**

```bash
# Sem autenticação (401)
curl http://localhost:8000/me

# Credenciais inválidas (401)
curl -u invalid:wrong http://localhost:8000/me

# Usuário comum tentando operação admin (403)
curl -u config:config123 -X POST \
  -H "Content-Type: application/json" \
  -d '{"min_age": 18, "max_age": 25}' \
  http://localhost:8000/age-groups/

# Operador tentando acessar admin (403)
curl -u operator:operator456 http://localhost:8000/admin/users
```

## 📁 Gerenciamento de Usuários

### Estrutura do Arquivo

O arquivo `users.json` deve seguir esta estrutura:

```json
{
  "users": [
    {
      "username": "string", // Nome do usuário (único)
      "password": "string", // Senha em texto plano
      "role": "admin|user", // Papel do usuário
      "description": "string" // Descrição do usuário
    }
  ],
  "metadata": {
    "version": "string", // Versão do arquivo
    "last_updated": "string", // Data da última atualização
    "description": "string" // Descrição do arquivo
  }
}
```

### Adicionando Novos Usuários

1. **Edite o arquivo** `src/enroll_api/app/config/users.json`
2. **Adicione o novo usuário** na lista `users`
3. **Recarregue os usuários** via endpoint ou reinicie a aplicação

```bash
# Recarregar usuários sem reiniciar
curl -u admin:secret123 -X POST http://localhost:8000/admin/users/reload
```

### Fallback para Variáveis de Ambiente

Se o arquivo `users.json` não for encontrado, o sistema usa as variáveis de ambiente como fallback:

```bash
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=secret123
BASIC_AUTH_USERS=admin:secret123,config:config123
```

## 🔒 Segurança

### Medidas Implementadas

1. **Proteção contra Timing Attacks**

   - Uso de `secrets.compare_digest()` para comparação de senhas

2. **Headers de Segurança**

   - `WWW-Authenticate: Basic` em respostas 401

3. **Validação Robusta**

   - Verificação de formato de credenciais
   - Tratamento de casos extremos

4. **Separação de Privilégios**
   - Roles distintos (admin/user)
   - Endpoints administrativos protegidos

### Recomendações de Produção

⚠️ **IMPORTANTE**: Basic Auth transmite credenciais em base64, que é facilmente decodificável.

**Para produção, recomenda-se:**

1. **HTTPS Obrigatório**
2. **Senhas Criptografadas** no arquivo JSON
3. **Arquivo de usuários protegido** (permissões 600)
4. **Rotação regular de credenciais**
5. **Monitoramento de acesso**

## 🛠️ Implementação Técnica

### Estrutura do Código

```
src/enroll_api/app/
├── auth/
│   ├── __init__.py
│   └── basic_auth.py          # Lógica de autenticação
├── config/
│   ├── config.py              # Configurações
│   └── users.json             # Arquivo de usuários
├── endpoints/
│   ├── admin.py               # Endpoints administrativos
│   ├── age_groups.py          # Endpoints protegidos
│   └── enrollment.py          # Endpoints protegidos
```

### Fluxo de Carregamento

1. **Inicialização** da aplicação
2. **Tentativa de carregar** usuários do arquivo JSON
3. **Fallback** para variáveis de ambiente se arquivo não existir
4. **Log** dos usuários carregados (sem senhas)
5. **Disponibilização** via endpoints administrativos

## 📚 Referências

- [RFC 7617 - HTTP Basic Authentication](https://tools.ietf.org/html/rfc7617)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 🔄 Próximos Passos

Para melhorar a segurança, considere implementar:

1. **Senhas criptografadas** (bcrypt, argon2)
2. **JWT Tokens** para autenticação stateless
3. **OAuth 2.0** para integração com provedores externos
4. **API Keys** para acesso programático
5. **Multi-factor Authentication (MFA)**
6. **Audit Logging** para rastreamento de acesso
