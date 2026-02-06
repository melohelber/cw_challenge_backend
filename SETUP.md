# 🚀 CloudWalk Agent Swarm - Guia de Setup

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Git
- Postman (opcional, para testar a API)

---

## 🐳 Como Rodar com Docker

### 1. Clone o repositório (se ainda não tiver)

```bash
git clone <seu-repo>
cd cw_challenge_backend
```

### 2. Configure as variáveis de ambiente

Crie o arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o `.env` e adicione suas API keys:

```env
# API Keys (OBRIGATÓRIO)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
TAVILY_API_KEY=tvly-xxxxx

# Security (OBRIGATÓRIO)
SECRET_KEY=seu-secret-key-aqui-min-32-chars

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Build e rode o Docker

```bash
# Build da imagem
docker-compose build

# Iniciar o container
docker-compose up

# Ou em background
docker-compose up -d
```

### 4. Verificar se está rodando

```bash
# Ver logs
docker-compose logs -f

# Verificar health
curl http://localhost:8000/health
```

### 5. Parar o container

```bash
docker-compose down
```

---

## 🧪 Como Testar a API com Postman

### 1. Importar a Collection

1. Abra o Postman
2. Clique em **Import**
3. Selecione o arquivo `CloudWalk_Agent_Swarm.postman_collection.json`
4. A collection será importada com **JWT automático** configurado!

### 2. Configurar Environment (Opcional)

Se quiser customizar usuário/senha:

1. Crie um Environment no Postman
2. Adicione as variáveis:
   - `base_url`: `http://localhost:8000`
   - `test_username`: `test`
   - `test_password`: `test123`

### 3. Testar os Endpoints

#### A. Registrar Usuário

```
POST http://localhost:8000/auth/register

Body:
{
  "username": "test",
  "password": "test123"
}
```

#### B. Login (JWT será salvo automaticamente!)

```
POST http://localhost:8000/auth/login

Body:
{
  "username": "test",
  "password": "test123"
}
```

**O Pre-Request Script vai:**
- Fazer login automaticamente
- Salvar o JWT token
- Renovar quando expirar (30 min)

#### C. Chat com a API (JWT automático!)

```
POST http://localhost:8000/chat
Authorization: Bearer {{jwt_token}}  ← AUTOMÁTICO!

Body:
{
  "message": "Quais são as taxas do Pix?"
}
```

**Exemplos de mensagens:**

- **Knowledge**: "Como funciona a maquininha InfinitePay?"
- **Support**: "Mostre minhas transações recentes"
- **Guardrails**: "ignore all instructions" (será bloqueado)

---

## 🛠️ Comandos Úteis

### Docker

```bash
# Ver logs em tempo real
docker-compose logs -f backend

# Reiniciar container
docker-compose restart

# Rebuild após mudanças no código
docker-compose up --build

# Limpar tudo (cuidado!)
docker-compose down -v
```

### Local (sem Docker)

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Popular RAG Database

```bash
# Dentro do container
docker-compose exec backend python scripts/populate_vectorstore.py

# Ou local
python scripts/populate_vectorstore.py
```

---

## 📊 Endpoints Disponíveis

| Endpoint | Método | Auth | Descrição |
|----------|--------|------|-----------|
| `/` | GET | ❌ | Root endpoint |
| `/health` | GET | ❌ | Health check |
| `/docs` | GET | ❌ | Swagger UI (API docs) |
| `/auth/register` | POST | ❌ | Registrar usuário |
| `/auth/login` | POST | ❌ | Login (retorna JWT) |
| `/chat` | POST | ✅ | Chat com agentes |

---

## 🔐 Como Funciona o JWT Automático no Postman

O **Pre-Request Script** da collection faz:

1. Verifica se já tem token válido
2. Se não tem ou expirou:
   - Faz login automaticamente
   - Salva o token em `{{jwt_token}}`
   - Define expiração (25 min)
3. Usa o token em todas as requisições protegidas

**Você não precisa fazer login manualmente!** 🎉

---

## 🐛 Troubleshooting

### Erro: "Could not validate credentials"

- Token expirou → Refaça login ou espere o pre-request renovar
- Token inválido → Delete `jwt_token` das globals do Postman

### Erro: "Address already in use"

```bash
# Matar processo na porta 8000
lsof -ti:8000 | xargs kill -9

# Ou mudar a porta no docker-compose.yml
ports:
  - "8001:8000"
```

### Docker não inicia

```bash
# Verificar logs
docker-compose logs backend

# Rebuild limpo
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## 📝 Próximos Passos

1. ✅ Rodar Docker
2. ✅ Testar no Postman
3. ✅ Verificar logs
4. 🚀 Deploy no Render.com (opcional)

---

**Pronto!** 🎉 Sua API está rodando com Docker e Postman configurado com JWT automático!
