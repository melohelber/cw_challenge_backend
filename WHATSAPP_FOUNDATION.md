# WHATSAPP FOUNDATION - Integração WhatsApp via UAZAPI

**Data de Criação:** 2026-02-09
**Status:** Planejamento
**Objetivo:** Integrar WhatsApp como segundo canal de mensagens usando UAZAPI (API não-oficial)

---

## INDICE

1. [Por que WhatsApp + UAZAPI](#1-por-que-whatsapp--uazapi)
2. [Arquitetura: Polling vs Webhook](#2-arquitetura-polling-vs-webhook)
3. [Fluxo Completo de Mensagens](#3-fluxo-completo-de-mensagens)
4. [Estrutura do Conector](#4-estrutura-do-conector)
5. [Variáveis de Ambiente](#5-variáveis-de-ambiente)
6. [Webhook: Payload e Eventos](#6-webhook-payload-e-eventos)
7. [Particularidades WhatsApp vs Telegram](#7-particularidades-whatsapp-vs-telegram)
8. [Dev (ngrok) vs Produção (Nuvem)](#8-dev-ngrok-vs-produção-nuvem)
9. [AÇÕES MANUAIS DO USUÁRIO](#9-ações-manuais-do-usuário)
10. [Checklist de Implementação](#10-checklist-de-implementação)

---

## 1. Por que WhatsApp + UAZAPI

### O Problema

O WhatsApp Business API oficial da Meta exige:
- Processo de aprovação empresarial (semanas)
- Conta Business verificada
- Custos por mensagem (modelo pay-per-conversation)
- Complexidade de setup (Facebook Business Manager, webhook verification, etc.)

### A Solução: UAZAPI

**UAZAPI** (https://uazapi.dev) é uma API não-oficial para WhatsApp que:
- Funciona conectando um número WhatsApp comum via QR Code
- Não precisa de aprovação da Meta
- Setup em minutos (criar conta, criar instância, escanear QR)
- R$138/mês para até 100 números (ou plano gratuito para testes)
- REST API simples para enviar/receber mensagens
- Webhooks para receber mensagens em tempo real

### Por que para este projeto?

Para o challenge da CloudWalk, UAZAPI permite demonstrar integração WhatsApp funcional sem burocracia. O conector segue o mesmo padrão channel-agnostic do Telegram: o backend não sabe que a mensagem veio do WhatsApp.

---

## 2. Arquitetura: Polling vs Webhook

Esta é a diferença fundamental entre o Telegram e o WhatsApp (UAZAPI).

### Telegram: Polling (Pull)

```
Nosso Bot (telegram_bot.py)              Telegram Servers
        |                                      |
        |--- "Tem mensagem nova?" ------------>|
        |<--- "Sim: 'Qual a taxa do Pix?'" ---|
        |                                      |
        |--- "Tem mensagem nova?" ------------>|
        |<--- "Nao, nenhuma" -----------------|
        |                                      |
        |--- "Tem mensagem nova?" ------------>|
        |<--- "Sim: 'E para R$1000?'" --------|
```

**Como funciona:**
- A library `python-telegram-bot` faz isso automaticamente (`application.run_polling()`)
- Nosso bot PERGUNTA ao Telegram se tem mensagens novas
- Nosso bot inicia a conexão, não precisa de URL pública
- Funciona atrás de firewall, NAT, qualquer rede

### WhatsApp (UAZAPI): Webhook (Push)

```
UAZAPI Cloud                         Nosso Servidor (whatsapp_bot.py)
     |                                          |
     |--- POST /webhook ---------------------->|
     |    {"message": "Qual a taxa do Pix?"}   |
     |                                          |
     |--- POST /webhook ---------------------->|
     |    {"message": "E para R$1000?"}        |
```

**Como funciona:**
- O UAZAPI ENVIA as mensagens para nós via HTTP POST
- Precisamos de um servidor HTTP rodando (Flask) com uma rota `/webhook`
- O UAZAPI precisa de uma URL para bater (ex: `https://meu-app.com/webhook`)
- Em desenvolvimento local, `localhost:5001` NÃO é acessível pela internet

### Por que a diferença importa?

| Aspecto | Polling (Telegram) | Webhook (WhatsApp) |
|---------|-------------------|-------------------|
| Quem inicia | Nosso bot pergunta | UAZAPI envia |
| Servidor HTTP | Não precisa | Precisa (Flask na porta 5001) |
| URL pública | Não precisa | Precisa (ngrok em dev, URL do deploy em prod) |
| Latência | Depende do intervalo de polling | Tempo real (push instantâneo) |
| Firewall | Sem problemas | Precisa que a porta esteja acessível |

### Diagrama Completo da Arquitetura

```
                    ┌─────────────────────────────────────────────┐
                    │            Docker Compose                    │
                    │                                              │
  Telegram User     │  ┌──────────────┐     ┌──────────────────┐  │
  ─── polling ──────│──│ telegram-bot  │────>│                  │  │
                    │  │ (porta N/A)   │     │    backend       │  │
                    │  └──────────────┘     │    (porta 8000)  │  │
                    │                       │                  │  │
  WhatsApp User     │  ┌──────────────┐     │  /chat (JWT)     │  │
  ── UAZAPI ────────│──│ whatsapp-bot │────>│  /auth/login     │  │
  ── webhook ───────│──│ (porta 5001) │     │  /auth/register  │  │
                    │  └──────────────┘     └──────────────────┘  │
                    │                                              │
                    │  Rede interna Docker: http://backend:8000    │
                    └─────────────────────────────────────────────┘
```

---

## 3. Fluxo Completo de Mensagens

### Mensagem Entrando (Usuário WhatsApp envia mensagem)

```
1. Usuário envia "Qual a taxa do Pix?" no WhatsApp
       |
2. WhatsApp Servers recebem a mensagem
       |
3. UAZAPI Cloud (conectado ao número via QR Code) detecta a mensagem
       |
4. UAZAPI faz POST /webhook no nosso servidor Flask:
   {
     "event": "messages.upsert",
     "data": {
       "key": {"remoteJid": "5511999998888@s.whatsapp.net", "fromMe": false},
       "pushName": "Helber",
       "message": {"conversation": "Qual a taxa do Pix?"}
     }
   }
       |
5. whatsapp_bot.py recebe o webhook:
   a) Verifica se não é duplicata (message_id)
   b) Verifica session timeout (envia welcome se necessário)
   c) Extrai: telefone, nome do contato, texto da mensagem
   d) Sanitiza mensagem (anti-injeção de nome)
       |
6. BackendClient envia para o backend:
   POST http://backend:8000/chat
   Headers: Authorization: Bearer {jwt_token}
   Body: {"message": "Qual a taxa do Pix?\n\n[User's real first name is: Helber]"}
       |
7. Backend processa (AgentOrchestrator):
   a) GuardrailsService verifica segurança
   b) RouterAgent classifica: KNOWLEDGE
   c) KnowledgeAgent busca no RAG + web
   d) Retorna resposta
       |
8. whatsapp_bot.py recebe a resposta:
   {"response": "A taxa do Pix na InfinitePay é...", "agent_used": "knowledge"}
       |
9. Formata resposta para WhatsApp (Markdown → WhatsApp formatting)
       |
10. UazapiClient envia via UAZAPI:
    POST https://api.uazapi.com/sendText
    Headers: apikey: {UAZAPI_API_TOKEN}
    Body: {"phone": "5511999998888", "message": "A taxa do Pix na InfinitePay é..."}
        |
11. UAZAPI Cloud envia para o WhatsApp
        |
12. Usuário recebe a resposta no WhatsApp
```

### Mensagem Saindo (Resposta)

```
whatsapp_bot.py
     |
     | POST /sendText
     v
UAZAPI REST API (api.uazapi.com)
     |
     v
WhatsApp Servers
     |
     v
Telefone do Usuário
```

---

## 4. Estrutura do Conector

### Arquivo: `connectors/whatsapp_bot.py` (~420 linhas)

O conector é um arquivo único (mesmo padrão do Telegram) com as seguintes seções:

#### 4.1. UazapiClient (classe nova - sem equivalente no Telegram)

Responsável por se comunicar com a API do UAZAPI para ENVIAR mensagens.

```
UazapiClient
├── send_text(phone, message)     → POST /sendText
├── get_instance_status()         → GET /status
└── _mask_phone(phone)            → "****8888" (privacidade nos logs)
```

**Autenticação**: Header `apikey` com o token da UAZAPI em toda requisição.

#### 4.2. BackendClient (cópia do Telegram)

Idêntico ao do `telegram_bot.py`. Responsável por autenticar com o backend via JWT e enviar mensagens para o endpoint `/chat`.

```
BackendClient
├── login()                       → POST /auth/login (JWT)
├── ensure_authenticated()        → Renova token se expirado
└── send_message(message, phone)  → POST /chat (Bearer token)
```

**Diferença do Telegram**: O user_id é prefixado com `whatsapp_` ao invés de `telegram_`.

#### 4.3. Funções de Formatação

```
format_for_whatsapp(text)    → Converte Markdown do Claude para formato WhatsApp
strip_all_formatting(text)   → Remove TODA formatação (fallback)
sanitize_and_enrich_message() → Anti-injeção de nome (mesma do Telegram)
extract_contact_name()       → Extrai nome do contato do webhook payload
```

**Formatação WhatsApp:**
- `*bold*` (asterisco simples)
- `_italic_` (underscore simples)
- `~strikethrough~` (til)
- ` ```code``` ` (três crases)
- Sem suporte a headings (#)

#### 4.4. Flask Webhook Server

```
Flask App (porta 5001)
├── POST /webhook     → Recebe mensagens do UAZAPI
├── GET  /webhook     → Health check / verificação
└── GET  /health      → Health check para Docker
```

#### 4.5. Lógica de Estado

```
Deduplicação          → Set de message_ids processados (max 1000)
Session Timeout       → Dict de phone → última mensagem (configurável)
Welcome Message       → Enviada na primeira msg ou após timeout
Thread Safety         → Lock para acesso concorrente (Flask threaded)
```

---

## 5. Variáveis de Ambiente

### Novas variáveis (adicionar ao `.env`):

```bash
# ============================================
# WhatsApp Bot via UAZAPI
# ============================================

# UAZAPI API (obter em uazapi.dev após criar instância)
UAZAPI_BASE_URL=https://api.uazapi.com          # Produção
# UAZAPI_BASE_URL=https://free.uazapi.dev       # Testes (gratuito)
UAZAPI_API_TOKEN=seu-token-da-uazapi-aqui        # OBRIGATÓRIO
UAZAPI_INSTANCE_ID=seu-instance-id-aqui           # OBRIGATÓRIO

# Segurança do webhook (opcional, mas recomendado)
UAZAPI_WEBHOOK_TOKEN=um-token-secreto-qualquer

# Bot user no backend (mesmo padrão do Telegram)
WHATSAPP_BOT_USERNAME=whatsapp_bot
WHATSAPP_BOT_PASSWORD=senha-do-bot-no-backend     # OBRIGATÓRIO

# Configuração
WHATSAPP_SESSION_TIMEOUT_MINUTES=10
WHATSAPP_WEBHOOK_PORT=5001
```

### Tabela resumo:

| Variável | Obrigatória | Default | De onde vem |
|----------|-------------|---------|-------------|
| `UAZAPI_BASE_URL` | Não | `https://api.uazapi.com` | Escolha: prod ou teste |
| `UAZAPI_API_TOKEN` | **Sim** | - | Dashboard UAZAPI |
| `UAZAPI_INSTANCE_ID` | **Sim** | - | Dashboard UAZAPI |
| `UAZAPI_WEBHOOK_TOKEN` | Não | `""` | Você inventa (segurança) |
| `WHATSAPP_BOT_USERNAME` | Não | `whatsapp_bot` | Fixo |
| `WHATSAPP_BOT_PASSWORD` | **Sim** | - | Você define ao registrar |
| `WHATSAPP_SESSION_TIMEOUT_MINUTES` | Não | `10` | Configurável |
| `WHATSAPP_WEBHOOK_PORT` | Não | `5001` | Configurável |

---

## 6. Webhook: Payload e Eventos

### Evento: Mensagem de Texto Recebida

```json
{
  "event": "messages.upsert",
  "instance": "seu-instance-id",
  "data": {
    "key": {
      "remoteJid": "5511999998888@s.whatsapp.net",
      "fromMe": false,
      "id": "ABCDEF123456789"
    },
    "pushName": "Helber Melo",
    "message": {
      "conversation": "Qual a taxa do Pix?"
    },
    "messageTimestamp": "1707500000"
  }
}
```

### Evento: Mensagem com Citação (Reply)

```json
{
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "5511999998888@s.whatsapp.net",
      "fromMe": false,
      "id": "GHIJKL789012345"
    },
    "message": {
      "extendedTextMessage": {
        "text": "E para valores acima de R$ 1000?",
        "contextInfo": {
          "quotedMessage": {
            "conversation": "A taxa do Pix é 0,99%"
          }
        }
      }
    }
  }
}
```

### Campos Importantes

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `event` | Tipo do evento | `messages.upsert` |
| `data.key.remoteJid` | Telefone + sufixo | `5511999998888@s.whatsapp.net` |
| `data.key.fromMe` | Se a mensagem é nossa | `false` (recebida) / `true` (enviada) |
| `data.key.id` | ID único da mensagem | `ABCDEF123456789` |
| `data.pushName` | Nome do contato | `Helber Melo` |
| `data.message.conversation` | Texto da mensagem | `Qual a taxa do Pix?` |
| `data.message.extendedTextMessage.text` | Texto de reply | `E para R$1000?` |

### Mensagens que IGNORAMOS

| Tipo | Como identificar | Por que ignorar |
|------|-----------------|-----------------|
| Nossas próprias | `fromMe: true` | Evita loop infinito |
| Grupos | `@g.us` no remoteJid | Fora do escopo |
| Imagens | `imageMessage` no message | Só processamos texto |
| Áudios | `audioMessage` no message | Só processamos texto |
| Vídeos | `videoMessage` no message | Só processamos texto |
| Stickers | `stickerMessage` no message | Só processamos texto |
| Documentos | `documentMessage` no message | Só processamos texto |
| Status/delivery | `message_status` no event | Não é mensagem |

> **Para mídia**: O bot responde educadamente "Desculpe, no momento só consigo processar mensagens de texto."

> **NOTA IMPORTANTE**: O formato exato do payload pode variar entre versões da UAZAPI. O conector terá logging detalhado do payload bruto para facilitar debug durante os primeiros testes.

---

## 7. Particularidades WhatsApp vs Telegram

| Aspecto | Telegram | WhatsApp (UAZAPI) |
|---------|----------|-------------------|
| **Recepção de mensagens** | Polling (library faz automaticamente) | Webhook (precisamos de servidor HTTP) |
| **Servidor próprio** | Não precisa | Flask + Gunicorn na porta 5001 |
| **ID do usuário** | `telegram_{user_id}` (ex: `telegram_123456`) | `whatsapp_{phone}` (ex: `whatsapp_5511999998888`) |
| **Autenticação na API** | Bot token na URL da library | Header `apikey` em cada request |
| **Formato bold** | `*text*` | `*text*` (igual) |
| **Formato código** | `` `code` `` (crase simples) | ` ```code``` ` (três crases) |
| **Mensagens de grupo** | Bot não recebe (por design) | Recebe, mas ignoramos (`@g.us`) |
| **Mensagens de mídia** | Só texto | Recebe mídia, respondemos "só texto" |
| **URL pública** | Não precisa (polling) | Precisa para webhook |
| **Thread safety** | Async event loop (serializado) | Lock (Flask é threaded) |
| **Library/SDK** | `python-telegram-bot` (completa) | Sem SDK - REST puro com `requests` |
| **Nome do contato** | `user.first_name` (sempre disponível) | `pushName` (pode ser vazio) |
| **Formato do telefone** | User ID numérico | E.164 sem + (ex: `5511999998888`) |
| **QR Code** | Não precisa (bot token do BotFather) | Precisa escanear para conectar número |
| **Reconexão** | Automática (library gerencia) | Manual se sessão expirar (novo QR) |

---

## 8. Dev (ngrok) vs Produção (Nuvem)

### Desenvolvimento Local (com ngrok)

**O problema**: UAZAPI está na internet, mas nosso servidor está em `localhost:5001`. O UAZAPI não consegue acessar `localhost`.

**A solução**: ngrok cria um túnel temporário.

```
Internet                          Sua Máquina
                                  ┌──────────────────────┐
UAZAPI Cloud ──── POST ────>     │ ngrok (túnel)         │
                                  │   https://abc123.     │
                                  │   ngrok.io            │
                                  │       │               │
                                  │       v               │
                                  │ localhost:5001        │
                                  │ (whatsapp_bot.py)     │
                                  │       │               │
                                  │       v               │
                                  │ localhost:8000        │
                                  │ (backend FastAPI)     │
                                  └──────────────────────┘
```

**Passos:**
```bash
# 1. Subir o projeto
docker compose up

# 2. Em outro terminal, rodar ngrok
ngrok http 5001

# 3. ngrok mostra:
#    Forwarding: https://abc123.ngrok-free.app -> http://localhost:5001

# 4. Copiar a URL e configurar no UAZAPI dashboard como webhook URL:
#    https://abc123.ngrok-free.app/webhook
```

**Limitações do ngrok gratuito:**
- URL muda toda vez que reinicia
- Precisa reconfigurar no UAZAPI dashboard a cada reinício
- Funciona perfeitamente para teste/desenvolvimento

### Produção (Deploy na Nuvem)

Quando deployar (Railway, Render, AWS, etc.), o serviço recebe uma URL pública automaticamente. Não precisa de ngrok.

```
Internet                          Cloud (Railway/Render/AWS)
                                  ┌──────────────────────┐
UAZAPI Cloud ──── POST ────>     │ https://meu-app.      │
                                  │ railway.app/webhook   │
                                  │       │               │
                                  │       v               │
                                  │ whatsapp-bot:5001     │
                                  │       │               │
                                  │       v               │
                                  │ backend:8000          │
                                  │ (rede interna Docker) │
                                  └──────────────────────┘
```

**Zero mudança no código.** Apenas atualiza a webhook URL no UAZAPI dashboard.

---

## 9. AÇÕES MANUAIS DO USUÁRIO

Estas são as ações que **VOCÊ** precisa fazer. O código eu implemento, mas estas etapas dependem de ações suas em plataformas externas.

---

### PASSO 1: Obter um Número de Telefone

Você precisa de um número WhatsApp para o bot. Opções:

**Opção A - Número Virtual (Recomendado para testes):**
- Use um app de números virtuais (ex: TextNow, Google Voice, ou um chip pré-pago)
- O número precisa receber SMS para ativar o WhatsApp

**Opção B - Chip Pré-pago:**
- Compre um chip de operadora
- Ative o WhatsApp nesse número
- Use exclusivamente para o bot

> **IMPORTANTE**: Não use seu número pessoal! O bot vai tomar conta do WhatsApp desse número.

---

### PASSO 2: Criar Conta na UAZAPI

1. Acesse https://uazapi.dev
2. Crie uma conta
3. Escolha o plano:
   - **Gratuito** (`free.uazapi.dev`) - para testes
   - **Pago** (`api.uazapi.com`) - R$138/mês, até 100 números

---

### PASSO 3: Criar Instância na UAZAPI

1. No dashboard da UAZAPI, clique em "Criar Instância"
2. Dê um nome (ex: "cloudwalk-bot")
3. Anote o **Instance ID** que será gerado
4. Anote o **API Token** da sua conta

> Esses dois valores vão no `.env` como `UAZAPI_INSTANCE_ID` e `UAZAPI_API_TOKEN`

---

### PASSO 4: Conectar o Número WhatsApp

1. No dashboard da UAZAPI, na sua instância, clique em "Conectar"
2. Um **QR Code** será exibido
3. No WhatsApp do telefone com o número do bot:
   - Vá em Configurações > Aparelhos Conectados > Conectar Aparelho
   - Escaneie o QR Code
4. Aguarde a conexão ser estabelecida (status: "connected")

> O WhatsApp do telefone precisa ficar online pelo menos até a sessão ser estabelecida. Depois, a UAZAPI mantém a conexão na nuvem.

---

### PASSO 5: Configurar Webhook URL

1. No dashboard da UAZAPI, na sua instância, vá em "Webhooks"
2. Configure a URL:
   - **Desenvolvimento**: URL do ngrok (ex: `https://abc123.ngrok-free.app/webhook`)
   - **Produção**: URL do deploy (ex: `https://meu-app.railway.app/webhook`)
3. Ative os eventos:
   - `messages.upsert` (obrigatório - mensagens recebidas)
   - `message_status` (opcional - confirmações de entrega)

---

### PASSO 6: Instalar ngrok (Apenas para Desenvolvimento)

```bash
# MacOS
brew install ngrok

# Linux
snap install ngrok

# Ou download direto: https://ngrok.com/download
```

Depois de instalar:
```bash
# Criar conta gratuita em ngrok.com e autenticar:
ngrok config add-authtoken SEU_TOKEN_DO_NGROK

# Rodar:
ngrok http 5001
```

---

### PASSO 7: Registrar User `whatsapp_bot` no Backend

Antes de rodar o conector, o user do bot precisa existir no backend:

```bash
# Com o backend rodando (docker compose up backend):
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "whatsapp_bot", "password": "SUA_SENHA_AQUI"}'
```

> A senha que você escolher aqui deve ir no `.env` como `WHATSAPP_BOT_PASSWORD`

---

### PASSO 8: Preencher o `.env`

Adicione estas variáveis ao seu arquivo `.env`:

```bash
# WhatsApp Bot via UAZAPI
UAZAPI_BASE_URL=https://api.uazapi.com
UAZAPI_API_TOKEN=cole-seu-token-aqui
UAZAPI_INSTANCE_ID=cole-seu-instance-id-aqui
UAZAPI_WEBHOOK_TOKEN=invente-um-token-secreto
WHATSAPP_BOT_USERNAME=whatsapp_bot
WHATSAPP_BOT_PASSWORD=mesma-senha-do-passo-7
WHATSAPP_SESSION_TIMEOUT_MINUTES=10
WHATSAPP_WEBHOOK_PORT=5001
```

---

### PASSO 9: Testar!

```bash
# 1. Subir tudo
docker compose up --build

# 2. Em outro terminal (apenas dev local)
ngrok http 5001

# 3. Configurar URL do ngrok no dashboard UAZAPI (Passo 5)

# 4. Enviar uma mensagem no WhatsApp para o número do bot

# 5. Verificar logs
docker compose logs -f whatsapp-bot
docker compose logs -f backend
```

---

### RESUMO: O que eu (Claude) faço vs O que você faz

| Quem | O que |
|------|-------|
| **Claude** | Cria `connectors/whatsapp_bot.py` |
| **Claude** | Cria `connectors/whatsapp_Dockerfile` |
| **Claude** | Atualiza `docker-compose.yml` |
| **Claude** | Atualiza `.env.example` |
| **Claude** | Atualiza `README.md` |
| **Você** | Obtém número de telefone |
| **Você** | Cria conta na UAZAPI |
| **Você** | Cria instância e conecta número (QR Code) |
| **Você** | Configura webhook URL |
| **Você** | Instala ngrok (dev) |
| **Você** | Registra user `whatsapp_bot` no backend |
| **Você** | Preenche `.env` com credenciais |

---

## 10. Checklist de Implementação

### Arquivos a Criar

- [ ] `connectors/whatsapp_bot.py` - Conector principal
  - [ ] UazapiClient (comunicação com UAZAPI REST API)
  - [ ] BackendClient (autenticação JWT + envio para /chat)
  - [ ] Funções de formatação (Markdown → WhatsApp)
  - [ ] Sanitização anti-injeção de nome
  - [ ] Flask webhook server (POST /webhook, GET /health)
  - [ ] Deduplicação de mensagens
  - [ ] Session timeout + welcome message
  - [ ] Filtro: ignora fromMe, grupos, mídia
  - [ ] Resposta educada para mensagens de mídia
  - [ ] Logging detalhado do payload (debug)
  - [ ] Tratamento de rate limit (HTTP 429)
  - [ ] Tratamento de mensagens longas (split)

- [ ] `connectors/whatsapp_Dockerfile` - Container Docker
  - [ ] Python 3.11 slim
  - [ ] Flask + Gunicorn + requests + dotenv
  - [ ] Health check
  - [ ] Gunicorn com 2 workers, timeout 60s

### Arquivos a Modificar

- [ ] `docker-compose.yml` - Adicionar serviço `whatsapp-bot`
  - [ ] Porta 5001:5001
  - [ ] Depends on: backend (service_healthy)
  - [ ] BACKEND_URL=http://backend:8000

- [ ] `.env.example` - Adicionar variáveis UAZAPI

- [ ] `README.md` - Adicionar seção WhatsApp
  - [ ] Diagrama Polling vs Webhook
  - [ ] Tabela comparativa Telegram vs WhatsApp
  - [ ] Instruções de configuração
  - [ ] Variáveis de ambiente

### Testes

- [ ] Mensagem de texto simples (deve processar e responder)
- [ ] Primeira mensagem (deve enviar welcome)
- [ ] Mensagem após timeout (deve enviar welcome)
- [ ] Mensagem de mídia (deve responder "só texto")
- [ ] Mensagem de grupo (deve ignorar)
- [ ] Mensagem própria/fromMe (deve ignorar)
- [ ] Mensagem duplicada (deve ignorar)
- [ ] Backend offline (deve responder com erro amigável)
- [ ] Docker Compose completo (todos os serviços sobem)

---

**Documento Mantido Por:** Claude Code Assistant
**Data de Criação:** 2026-02-09
**Status:** Aguardando ações manuais do usuário + implementação do código
