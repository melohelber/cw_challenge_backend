# CloudWalk Agent Swarm Challenge - FOUNDATION

**Project:** Agent Swarm System for InfinitePay Customer Support
**Company:** CloudWalk
**Interviewer:** Leonardo Frizzo (Head of Team)
**CEO:** Luiz Silva
**Goal:** 10/10 submission - production-ready code demonstrating senior-level skills

---

## 🎯 Mission Statement

Build an Agent Swarm system that demonstrates:
1. **Technical Excellence:** Production-ready code, SOLID principles, clean architecture
2. **Agent Expertise:** Multiple AI agents collaborating via LangChain/LangGraph
3. **RAG Implementation:** Knowledge retrieval from InfinitePay documentation
4. **Security:** JWT authentication, input validation, secure practices
5. **DevOps:** Docker, deployment-ready, comprehensive documentation

**Deliverables:**
- ✅ Backend API (FastAPI) - Deployed on Render.com
- ✅ Frontend Web UI (Next.js) - Deployed on Vercel
- ✅ Telegram Bot (Bonus) - Pluggable messaging architecture
- ✅ Docker setup working out of the box
- ✅ Comprehensive tests (>80% coverage)
- ✅ Impeccable documentation

---

## 📋 Project Constraints & Code Quality Standards

### ⚠️ CRITICAL RULES - NO EXCEPTIONS

#### 1. NO Inline Comments
```python
# ❌ BAD
def process_message(msg):
    # Check if message is valid
    if not msg:
        return None
    # Process the message
    return msg.upper()

# ✅ GOOD
def process_message(msg: str) -> str | None:
    if not self._is_valid_message(msg):
        return None

    return self._transform_to_uppercase(msg)

def _is_valid_message(self, msg: str) -> bool:
    return bool(msg and msg.strip())

def _transform_to_uppercase(self, msg: str) -> str:
    return msg.upper()
```

#### 2. English ONLY for Code
- ✅ Variable names, function names, class names: English
- ✅ Logs, error messages, docstrings: English
- ✅ Code documentation: English
- ✅ User-facing responses: Portuguese (when user speaks PT-BR)

```python
# ❌ BAD
def processar_mensagem(mensagem: str) -> str:
    """Processa mensagem do usuário"""
    pass

# ✅ GOOD
def process_message(message: str) -> str:
    """Processes user message and returns agent response"""
    pass
```

#### 3. Self-Documenting Code
- Clear, descriptive names
- Small, focused functions
- Type hints everywhere
- Pydantic models for validation

```python
# ❌ BAD
def p(m, u):
    return f"{m} - {u}"

# ✅ GOOD
def format_conversation_entry(message: str, user_id: str) -> str:
    return f"{message} - {user_id}"
```

#### 4. Architecture Standards
- **SOLID principles**
- **Dependency Injection** (FastAPI dependencies)
- **Separation of Concerns** (routes → orchestrator → agents → tools)
- **Design Patterns** where appropriate
- **Type hints** everywhere (Python 3.11+)

#### 5. Security Standards
- ✅ API keys in `.env` (NEVER hardcoded)
- ✅ `.env` git-ignored, `.env.example` committed
- ✅ Validate environment variables on startup
- ✅ Mask API keys in logs (show only last 4 chars)
- ✅ CORS properly configured
- ✅ Input validation (Pydantic)
- ✅ JWT tokens expire (30 minutes)
- ✅ Passwords hashed with bcrypt

---

## 🏗️ Complete Repository Structure

```
cw_challenge_backend/
│
├── FOUNDATION.md                  ← THIS FILE
├── README.md                      ← Main documentation
├── requirements.txt               ← Python dependencies
├── pytest.ini                     ← Pytest configuration
├── .env.example                   ← Environment variables template
├── .gitignore                     ← Git ignore rules
├── Dockerfile                     ← Docker build configuration
├── docker-compose.yml             ← Local development setup
│
├── app/                           ← Main application package
│   ├── __init__.py
│   ├── main.py                    ← FastAPI application entry point
│   ├── config.py                  ← Environment configuration (pydantic-settings)
│   │
│   ├── api/                       ← API layer (routes + dependencies)
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           ← POST /auth/register, /auth/login
│   │   │   ├── chat.py           ← POST /chat (protected)
│   │   │   └── history.py        ← GET /history (protected)
│   │   │
│   │   └── dependencies.py        ← Dependency injection (get_current_user, etc)
│   │
│   ├── core/                      ← Core business logic
│   │   ├── __init__.py
│   │   ├── database.py           ← SQLAlchemy engine, session, Base
│   │   ├── security.py           ← JWT encode/decode, password hashing
│   │   ├── orchestrator.py       ← Coordinates agent workflow
│   │   │
│   │   ├── agents/               ← AI Agents (LangChain)
│   │   │   ├── __init__.py
│   │   │   ├── base.py           ← Abstract BaseAgent class
│   │   │   ├── router.py         ← RouterAgent (classifies intent)
│   │   │   ├── knowledge.py      ← KnowledgeAgent (RAG + web search)
│   │   │   ├── support.py        ← SupportAgent (uses tools)
│   │   │   └── slack.py          ← SlackAgent (escalation, mocked)
│   │   │
│   │   └── tools/                ← Agent tools (mocked data)
│   │       ├── __init__.py
│   │       ├── user_lookup.py
│   │       ├── transaction_history.py
│   │       ├── account_status.py
│   │       └── transfer_troubleshoot.py
│   │
│   ├── services/                  ← External services & infrastructure
│   │   ├── __init__.py
│   │   ├── anthropic_client.py   ← Anthropic API wrapper
│   │   ├── vector_store.py       ← ChromaDB for RAG embeddings
│   │   ├── web_search.py         ← Tavily API integration
│   │   ├── cache.py              ← In-memory cache (TTL: 1 hour)
│   │   ├── guardrails.py         ← Content moderation
│   │   ├── user_store.py         ← User CRUD (SQLAlchemy)
│   │   └── history_store.py      ← Conversation CRUD (SQLAlchemy)
│   │
│   ├── models/                    ← Data models
│   │   ├── __init__.py
│   │   ├── database/             ← SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py          ← User table schema
│   │   │   └── conversation.py  ← Conversations table schema
│   │   │
│   │   └── schemas/              ← Pydantic schemas (API)
│   │       ├── __init__.py
│   │       ├── requests.py       ← Request models (ChatRequest, etc)
│   │       ├── responses.py      ← Response models (ChatResponse, etc)
│   │       ├── user.py           ← User models (UserCreate, UserResponse)
│   │       └── token.py          ← Token models (TokenResponse)
│   │
│   └── utils/                     ← Utilities
│       ├── __init__.py
│       ├── logging.py            ← Structured logging setup
│       └── exceptions.py         ← Custom exception classes
│
├── connectors/                    ← Messaging connectors (pluggable)
│   ├── __init__.py
│   ├── telegram_bot.py           ← Telegram bot (primary)
│   └── whatsapp_bot.py           ← WhatsApp bot (future, placeholder)
│
├── tests/                         ← Test suite
│   ├── __init__.py
│   ├── conftest.py               ← Pytest fixtures
│   ├── unit/                     ← Unit tests
│   │   ├── test_agents.py
│   │   ├── test_tools.py
│   │   └── test_services.py
│   │
│   └── integration/              ← Integration tests
│       ├── test_auth_flow.py
│       ├── test_chat_flow.py
│       └── test_agent_orchestration.py
│
├── data/                          ← Data storage (git-ignored)
│   ├── .gitkeep
│   ├── app.db                    ← SQLite database (users + conversations)
│   └── vectorstore/              ← ChromaDB embeddings
│
└── scripts/                       ← Utility scripts
    ├── scrape_infinitepay.py     ← Scrape InfinitePay website
    └── seed_vectorstore.py       ← Populate ChromaDB with scraped data
```

---

## 🔧 Technology Stack (Final Decisions)

### Backend
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Language** | Python 3.11+ | CloudWalk uses Python, type hints, modern features |
| **Framework** | FastAPI | High performance, auto-docs, async, type validation |
| **Agent Framework** | LangChain + LangGraph | Industry standard for agent orchestration |
| **LLM Provider** | Anthropic Claude 4.5 | Available API key, excellent reasoning |
| **Database** | SQLite + SQLAlchemy | Simple, production-ready, easy migration to PostgreSQL |
| **Vector DB** | ChromaDB | Lightweight, perfect for RAG, easy setup |
| **Authentication** | JWT (manual) | Demonstrates security skills, no external dependencies |
| **Password Hashing** | bcrypt | Industry standard, secure |
| **Web Search** | Tavily API | $5 free credits, simple integration |
| **Container** | Docker + Docker Compose | Easy local dev, deployment-ready |

### Frontend
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Framework** | Next.js + TypeScript | Modern, SSR, easy Vercel deploy |
| **Deploy** | Vercel | Zero config, automatic HTTPS, edge functions |
| **Styling** | TailwindCSS (TBD) | Fast development, modern UI |

### Messaging (Bonus)
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Primary** | Telegram Bot API | Official API, no QR code, free, stable |
| **Future** | WhatsApp (WAHA/Z-API) | Pluggable architecture, easy to add later |
| **Architecture** | Channel-agnostic connectors | Backend doesn't know channel, clean separation |

### Deploy
| Component | Platform | Justification |
|-----------|-----------|---------------|
| **Backend** | Render.com | Free tier, env vars dashboard, Docker support |
| **Frontend** | Vercel | Automatic Next.js deployment, HTTPS, CDN |
| **Database** | Included in Render | SQLite file mounted as volume |

---

## 🏛️ Architecture Design

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Channels                            │
│  (Web UI / Telegram Bot / WhatsApp Bot / Swagger)          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /chat
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Core)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Authentication (JWT validation)                   │  │
│  │  2. Guardrails (content moderation)                   │  │
│  │  3. Orchestrator (coordinates agents)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Router Agent                             │
│  "Analyzes message intent, decides which agent to call"    │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬───────────────────┐
        ↓                ↓                ↓                   ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────────┐
│  Knowledge   │ │   Support    │ │    Slack     │ │  [Future      │
│    Agent     │ │    Agent     │ │    Agent     │ │   Agents]     │
│  (RAG+Web)   │ │   (Tools)    │ │ (Escalation) │ │               │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └───────────────┘
       │                │                │
       │ ChromaDB       │ 4 Mocked Tools │ Logs (mocked)
       │ Tavily API     │                │
       ↓                ↓                ↓
┌─────────────────────────────────────────────────────────────┐
│                   Aggregated Response                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Save to database (conversations table)            │  │
│  │  2. Return to user                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Channel-Agnostic Architecture (Pluggable Connectors)

**CORE PRINCIPLE:** Backend doesn't know which channel the message came from.

```
┌──────────────────────────────────────────┐
│       FastAPI Backend (Core)             │
│  POST /chat, GET /history, etc.          │
│  Channel-agnostic ← Same for all         │
└────────────┬─────────────────────────────┘
             │ HTTP REST API
             │
   ┌─────────┼─────────┬──────────┬──────────┐
   ↓         ↓         ↓          ↓          ↓
┌──────┐ ┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Web  │ │Telegram │ │WhatsApp│ │Swagger │ │ Future │
│ UI   │ │  Bot    │ │  Bot   │ │  UI    │ │Channels│
└──────┘ └─────────┘ └────────┘ └────────┘ └────────┘
```

**How to switch channels:**

```bash
# Today: Telegram
MESSAGING_CHANNEL=telegram
TELEGRAM_BOT_TOKEN=123456:ABC...
python connectors/telegram_bot.py

# Tomorrow: WhatsApp (if time permits)
MESSAGING_CHANNEL=whatsapp
WHATSAPP_API_URL=http://waha.yourserver.com
python connectors/whatsapp_bot.py

# Backend doesn't change! Just swap the connector.
```

**Benefits:**
1. ✅ Separation of Concerns (Backend = logic, Connectors = I/O)
2. ✅ Easy Testing (test backend via Swagger independently)
3. ✅ Scalability (add Slack, Discord, email, etc without touching core)
4. ✅ Maintainability (bug in Telegram? Only fix telegram_bot.py)

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    agent_used VARCHAR(50),              -- 'router', 'knowledge', 'support', 'slack'
    metadata JSON,                        -- Additional context (tools used, etc)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
```

**Relationships:**
- `User` → `Conversation` (1:N)
- User can have many conversations
- Deleting user cascades to conversations

---

## 🤖 Agent Specifications

### 1. Router Agent

**Responsibility:** Analyze incoming message and route to appropriate agent

**Input:**
```python
{
    "message": "Qual a taxa do Pix?",
    "user_id": "user123",
    "conversation_history": []  # Optional context
}
```

**Output:**
```python
{
    "target_agent": "knowledge",  # or "support", "slack"
    "confidence": 0.95,
    "reasoning": "User is asking about product features (Pix fees)"
}
```

**Classification Logic:**
- **KNOWLEDGE:** Product info, features, pricing, "how does X work", general info
- **SUPPORT:** User-specific issues, account problems, transaction errors, "my transfer failed"
- **SLACK:** Escalation needed, can't handle, out of scope, frustrated user

**Implementation Pattern:**
```python
# Few-shot examples for prompt
CLASSIFICATION_EXAMPLES = """
Examples:
- "What are the Pix fees?" → KNOWLEDGE (product info)
- "How do I create an account?" → KNOWLEDGE (product feature)
- "My transfer failed" → SUPPORT (user issue)
- "I can't log in" → SUPPORT (technical issue)
- "Talk to a human" → SLACK (escalation)
- "Who won the game yesterday?" → KNOWLEDGE (off-topic, but try to answer)
"""
```

---

### 2. Knowledge Agent

**Responsibility:** Answer questions using RAG (InfinitePay docs) + web search fallback

**Data Sources:**
1. **Primary:** ChromaDB vector store (InfinitePay website)
2. **Fallback:** Tavily API (general web search)

**RAG Pipeline:**
```
User Query
    ↓
Embed query (Anthropic embeddings)
    ↓
Search ChromaDB (top_k=5, threshold=0.7)
    ↓
Found relevant chunks?
    ├─ YES → Use RAG context + Claude to generate answer
    └─ NO → Fallback to Tavily web search
    ↓
Return answer (Portuguese if user spoke PT-BR)
```

**InfinitePay Pages to Scrape:**
```
https://www.infinitepay.io/
https://www.infinitepay.io/maquininha
https://www.infinitepay.io/conta-digital
https://www.infinitepay.io/pix
https://www.infinitepay.io/sobre
https://www.infinitepay.io/ajuda
```

**Caching Strategy:**
- Cache key: `hash(query + language)`
- TTL: 1 hour
- Invalidation: Manual (or after 1 hour)

---

### 3. Support Agent

**Responsibility:** Handle user-specific support queries using tools

**Tools (4 Mocked Tools - REQUIRED):**

#### Tool 1: User Lookup
```python
def user_lookup(user_id: str) -> dict:
    """
    Fetch user account information

    Use when user asks:
    - "What's my account status?"
    - "Am I verified?"
    - "Show my profile"

    Returns: name, email, account_status, verification_level
    """
    # Mocked data (includes Luiz Silva and Leonardo Frizzo!)
    return {
        "user_id": user_id,
        "name": "Luiz Silva",  # Personalized!
        "email": "luiz.silva@cloudwalk.io",
        "account_status": "active",
        "verification_level": "full",
        "created_at": "2024-01-15"
    }
```

#### Tool 2: Transaction History
```python
def transaction_history(user_id: str, limit: int = 5) -> list:
    """
    Retrieve recent transactions

    Use when user asks:
    - "Show my recent transactions"
    - "What did I spend on?"
    - "Transaction history"

    Returns: list of transactions with amount, date, merchant
    """
    return [
        {"id": "tx_001", "amount": 150.00, "merchant": "Padaria", "date": "2026-02-05"},
        {"id": "tx_002", "amount": 50.00, "merchant": "Uber", "date": "2026-02-04"},
        # ...
    ]
```

#### Tool 3: Account Status
```python
def account_status(user_id: str) -> dict:
    """
    Check account status (active/blocked/suspended)

    Use when user asks:
    - "Why can't I transfer money?"
    - "Is my account blocked?"
    - "Account status"

    Returns: status, reason (if blocked), actions_required
    """
    return {
        "status": "active",
        "can_send": True,
        "can_receive": True,
        "daily_limit": 5000.00,
        "used_today": 150.00
    }
```

#### Tool 4: Transfer Troubleshoot
```python
def transfer_troubleshoot(user_id: str, transaction_id: str) -> dict:
    """
    Diagnose transfer issues

    Use when user asks:
    - "My transfer failed, why?"
    - "Why is my Pix not working?"
    - "Troubleshoot transaction tx_123"

    Returns: status, error_code, resolution_steps
    """
    return {
        "transaction_id": transaction_id,
        "status": "failed",
        "error_code": "INSUFFICIENT_FUNDS",
        "resolution": "Your account balance is insufficient. Please add funds and try again.",
        "support_ticket": "TKT-2026-001"
    }
```

**IMPORTANT:** Include "Luiz Silva" and "Leonardo Frizzo" in mocked data to personalize the demo!

---

### 4. Slack Agent (Bonus - Mocked)

**Responsibility:** Escalate to human support (simulated)

**When to Escalate:**
- User explicitly asks for human: "Talk to a human", "Speak to someone"
- Router confidence < 0.5 (can't classify)
- User frustrated (detected by sentiment)
- Out of scope queries

**Implementation:**
```python
def escalate_to_slack(message: str, user_id: str, reason: str) -> dict:
    """
    Escalate to human support (mocked - just logs)

    In production, would:
    - Send Slack message to #support channel
    - Create Zendesk ticket
    - Email support team

    For demo: Just log and return ticket ID
    """
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    logger.info(f"🎫 ESCALATION | Ticket: {ticket_id} | User: {user_id} | Reason: {reason}")
    # Would send to Slack here

    return {
        "escalated": True,
        "ticket_id": ticket_id,
        "estimated_response_time": "15 minutes",
        "message": "Seu caso foi encaminhado para um especialista. Ticket: {ticket_id}"
    }
```

---

## 🔐 Authentication & Security

### Bot Authentication (Telegram) - FINAL DECISION ⭐

**Decision:** Bot uses same JWT authentication as frontend (NO special routes!)

**How it works:**

1. **Bot has its own account** (user "telegram_bot" in backend)
2. **Bot logs in once** on startup (gets JWT)
3. **JWT auto-renews** every 25 minutes (expires at 30)
4. **Same `/chat` endpoint** (no `/internal` routes needed!)
5. **User never logs in** (zero friction, just send messages)

**Architecture:**
```
Frontend Web:
  User logs in → JWT → POST /chat with user JWT
  ✅ Works!

Telegram Bot:
  Bot logs in → JWT → POST /chat with BOT JWT
  ✅ Same endpoint, same validation!
```

**Benefits:**
- ✅ Zero code duplication (no special routes)
- ✅ Production-ready (bots are clients like any other)
- ✅ JWT expires & auto-renews (secure)
- ✅ Scalable (WhatsApp bot, Slack bot = same pattern)
- ✅ Easy debugging (bot = user "telegram_bot" in logs)

**Implementation:**
```python
# connectors/telegram_bot.py
class BackendClient:
    def __init__(self):
        self.bot_username = "telegram_bot"
        self.bot_password = os.getenv("BOT_PASSWORD")
        self.jwt_token = None
        self.token_expires_at = None

    def login(self):
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username": self.bot_username, "password": self.bot_password}
        )
        self.jwt_token = response.json()["access_token"]
        self.token_expires_at = datetime.now() + timedelta(minutes=25)
        logger.info("Bot authenticated successfully")

    def ensure_authenticated(self):
        if not self.jwt_token or datetime.now() >= self.token_expires_at:
            logger.info("JWT expired, renewing token")
            self.login()

    def send_message(self, message: str, user_id: str):
        self.ensure_authenticated()

        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": message, "user_id": f"telegram_{user_id}"},
            headers={"Authorization": f"Bearer {self.jwt_token}"}
        )
        return response.json()
```

**Setup (one-time):**
```bash
# 1. Create bot user in backend
curl -X POST http://localhost:8000/auth/register \
  -d '{"username":"telegram_bot","password":"super-secret-bot-password"}'

# 2. Add to .env (bot connector)
BOT_USERNAME=telegram_bot
BOT_PASSWORD=super-secret-bot-password
TELEGRAM_BOT_TOKEN=123456:ABC...  # From @BotFather
```

**JWT Renewal Timeline:**
```
Time 0:00 - Bot starts, logs in → JWT valid for 30min
Time 0:05 - User message → JWT still valid (uses current)
Time 0:25 - User message → JWT expired! Auto-renews → New JWT
Time 0:30 - User message → JWT valid (renewed at 0:25)
... auto-renews every 25 minutes forever ...
```

**Why 25min not 30min?**
- JWT expires at 30min (backend)
- Bot renews at 25min (5min safety margin)
- Avoids expiring mid-request

---

### JWT Authentication Flow (Web Frontend)

```
1. User Registration
   POST /auth/register
   Body: {"username": "luiz", "password": "secret123"}
   ↓
   - Validate input (Pydantic)
   - Check username doesn't exist
   - Hash password (bcrypt, cost=12)
   - Save to database
   - Return success (no token yet)

2. User Login
   POST /auth/login
   Body: {"username": "luiz", "password": "secret123"}
   ↓
   - Validate input
   - Find user by username
   - Verify password (bcrypt)
   - Generate JWT token (expires in 30min)
   - Return token

3. Protected Endpoint
   POST /chat
   Headers: {"Authorization": "Bearer <token>"}
   ↓
   - Extract token from header
   - Verify JWT signature
   - Check expiration
   - Extract user_id from payload
   - Proceed with request
```

### JWT Token Structure

```python
# Payload
{
    "sub": "user123",           # User ID
    "username": "luiz",         # Username
    "exp": 1707217200,         # Expiration (30 minutes)
    "iat": 1707215400,         # Issued at
    "type": "access"           # Token type
}

# Signature: HMAC-SHA256(header + payload, SECRET_KEY)
```

### Security Checklist

- ✅ Passwords never stored in plaintext
- ✅ Bcrypt cost factor: 12 rounds
- ✅ JWT tokens expire after 30 minutes
- ✅ SECRET_KEY in environment variable (min 32 chars)
- ✅ API keys masked in logs: `sk-ant-***1234`
- ✅ CORS configured (allow specific origins)
- ✅ Input validation (Pydantic models)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Rate limiting (consider if needed)

---

## 📝 Logging Requirements

### Logging Philosophy

**CRITICAL**: Every use case entry point MUST be logged. This is non-negotiable for production systems.

**Rules:**
- ✅ **English only** for all log messages
- ✅ **Log every use case entry** (no exceptions)
- ✅ **Structured logging** (Python's logging module, not print statements)
- ✅ **Consistent format**: `"User [user_id] called [endpoint/action]"`
- ✅ **Mask sensitive data** (API keys, passwords, tokens)
- ✅ **Include context** (timestamp, log level, module name)

### Log Format

```python
# Standard format for use case entry
logger.info(f"User [{user_id}] called {endpoint}")

# With additional context
logger.info(f"User [{user_id}] called {endpoint} with message: '{message[:50]}...'")

# Error format
logger.error(f"User [{user_id}] failed {endpoint}: {error_message}")
```

### Implementation (utils/logging.py)

```python
import logging
import sys
from typing import Any

def setup_logging(log_level: str = "INFO"):
    """
    Configure structured logging for the application.

    Format: [TIMESTAMP] [LEVEL] [MODULE] Message
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

def mask_api_key(api_key: str) -> str:
    """Mask API key, showing only last 4 characters."""
    if not api_key or len(api_key) < 8:
        return "***"
    return f"{api_key[:7]}***{api_key[-4:]}"

def log_request(user_id: str, endpoint: str, **kwargs):
    """Standard log format for use case entries."""
    logger = logging.getLogger("api")

    # Build context string
    context_parts = [f"{k}={v}" for k, v in kwargs.items() if v]
    context = f" ({', '.join(context_parts)})" if context_parts else ""

    logger.info(f"User [{user_id}] called {endpoint}{context}")
```

### Logging Examples by Endpoint

#### 1. POST /auth/register
```python
from utils.logging import log_request

@router.post("/auth/register")
async def register(request: RegisterRequest):
    log_request(
        user_id="anonymous",
        endpoint="/auth/register",
        username=request.username
    )
    # ... registration logic
```

**Log Output:**
```
2026-02-06 14:30:15 [INFO] [api] User [anonymous] called /auth/register (username=john_doe)
```

#### 2. POST /auth/login
```python
@router.post("/auth/login")
async def login(request: LoginRequest):
    log_request(
        user_id="anonymous",
        endpoint="/auth/login",
        username=request.username
    )
    # ... authentication logic

    logger.info(f"User [{user.user_id}] authenticated successfully")
```

**Log Output:**
```
2026-02-06 14:31:20 [INFO] [api] User [anonymous] called /auth/login (username=john_doe)
2026-02-06 14:31:21 [INFO] [api] User [usr_123abc] authenticated successfully
```

#### 3. POST /chat (Protected Endpoint)
```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    log_request(
        user_id=current_user_id,
        endpoint="/chat",
        message_preview=request.message[:50]
    )

    # ... agent orchestration

    logger.info(f"User [{current_user_id}] received response from {agent_name}")
```

**Log Output:**
```
2026-02-06 14:35:10 [INFO] [api] User [usr_123abc] called /chat (message_preview=What are the fees for Pix transfers?)
2026-02-06 14:35:12 [INFO] [orchestrator] User [usr_123abc] routed to KnowledgeAgent
2026-02-06 14:35:14 [INFO] [api] User [usr_123abc] received response from KnowledgeAgent
```

#### 4. GET /history (Protected Endpoint)
```python
@router.get("/history")
async def get_history(
    current_user_id: str = Depends(get_current_user_id),
    limit: int = 20
):
    log_request(
        user_id=current_user_id,
        endpoint="/history",
        limit=limit
    )
    # ... fetch conversations
```

**Log Output:**
```
2026-02-06 14:40:30 [INFO] [api] User [usr_123abc] called /history (limit=20)
```

#### 5. Telegram Bot Messages
```python
# connectors/telegram_bot.py
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user_id = str(update.effective_user.id)
    user_id = f"telegram_{telegram_user_id}"
    message = update.message.text

    logger.info(f"User [{user_id}] sent message via Telegram: '{message[:50]}...'")

    # ... send to backend

    logger.info(f"User [{user_id}] received response via Telegram")
```

**Log Output:**
```
2026-02-06 14:45:00 [INFO] [telegram] User [telegram_12345678] sent message via Telegram: 'Como funciona o Pix no InfinitePay?...'
2026-02-06 14:45:02 [INFO] [telegram] User [telegram_12345678] received response via Telegram
```

### Sensitive Data Masking

**CRITICAL**: Never log sensitive data in plaintext.

```python
from utils.logging import mask_api_key

# ❌ WRONG
logger.info(f"Using API key: {api_key}")

# ✅ CORRECT
logger.info(f"Using API key: {mask_api_key(api_key)}")
# Output: "Using API key: sk-ant-***1234"

# ❌ WRONG
logger.info(f"User password: {password}")

# ✅ CORRECT
logger.info(f"User password validation: {'successful' if valid else 'failed'}")

# ❌ WRONG
logger.info(f"JWT token: {jwt_token}")

# ✅ CORRECT
logger.info(f"JWT token generated for user [{user_id}]")
```

### Error Logging

```python
from utils.logging import log_request

try:
    log_request(user_id=current_user_id, endpoint="/chat")
    result = orchestrator.process(message, user_id)
except HTTPException as e:
    logger.error(f"User [{current_user_id}] failed /chat: {e.detail}")
    raise
except Exception as e:
    logger.error(f"User [{current_user_id}] failed /chat: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Log Output:**
```
2026-02-06 15:00:10 [INFO] [api] User [usr_123abc] called /chat
2026-02-06 15:00:11 [ERROR] [api] User [usr_123abc] failed /chat: Agent orchestration timeout
```

### Log Levels

| Level | Usage |
|-------|-------|
| **INFO** | Use case entries, successful operations, state changes |
| **WARNING** | Recoverable issues (cache miss, fallback used, retry attempts) |
| **ERROR** | Failed operations, exceptions, authentication failures |
| **DEBUG** | Detailed flow (agent reasoning, tool calls, RAG retrieval) - only in development |

### Configuration

```python
# main.py
from utils.logging import setup_logging
from config import settings

# Initialize logging on startup
setup_logging(log_level=settings.LOG_LEVEL)

logger = logging.getLogger("api")
logger.info("CloudWalk Agent Swarm started")
logger.info(f"Environment: {settings.ENVIRONMENT}")
logger.info(f"Anthropic API key: {mask_api_key(settings.ANTHROPIC_API_KEY)}")
```

**Startup Log Output:**
```
2026-02-06 12:00:00 [INFO] [api] CloudWalk Agent Swarm started
2026-02-06 12:00:00 [INFO] [api] Environment: production
2026-02-06 12:00:00 [INFO] [api] Anthropic API key: sk-ant-***xyz9
```

---

## 📦 Environment Variables

### `.env.example` (committed to git)

```bash
# ============================================
# CloudWalk Agent Swarm - Environment Variables
# ============================================

# CRITICAL: Copy this to .env and fill in real values
# NEVER commit .env to git!

# -------------------- Required --------------------

# Anthropic API Key (get from: https://console.anthropic.com/)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Tavily API Key (get from: https://tavily.com/)
TAVILY_API_KEY=tvly-your-key-here

# JWT Secret (generate: openssl rand -hex 32)
SECRET_KEY=your-secret-key-min-32-chars

# -------------------- Optional --------------------

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false

# Database
DATABASE_URL=sqlite:///./data/app.db

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,https://cloudwalk-frontend.vercel.app

# Messaging (Telegram Bot)
MESSAGING_ENABLED=true
MESSAGING_CHANNEL=telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF-your-token

# -------------------- Production --------------------

# Set these in Render.com dashboard:
# - ANTHROPIC_API_KEY
# - TAVILY_API_KEY
# - SECRET_KEY
# - CORS_ORIGINS (frontend URL)
```

### Configuration Loading (Pydantic Settings)

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Required
    ANTHROPIC_API_KEY: str
    TAVILY_API_KEY: str
    SECRET_KEY: str

    # Optional with defaults
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./data/app.db"
    CORS_ORIGINS: str = "http://localhost:3000"

    MESSAGING_ENABLED: bool = False
    MESSAGING_CHANNEL: str = "telegram"
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_required(self):
        """Validate API keys on startup"""
        if not self.ANTHROPIC_API_KEY.startswith("sk-ant-"):
            raise ValueError("Invalid ANTHROPIC_API_KEY format")

        if not self.TAVILY_API_KEY.startswith("tvly-"):
            raise ValueError("Invalid TAVILY_API_KEY format")

        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")

settings = Settings()
settings.validate_required()
```

---

## 📝 Implementation Phases (Step-by-Step)

### Phase 1: Project Setup (Day 1 - Morning)

**Goal:** Working FastAPI app with database, auth, and basic structure

```bash
# 1. Create directory structure
mkdir -p app/{api/routes,core/{agents,tools},services,models/{database,schemas},utils}
mkdir -p tests/{unit,integration}
mkdir -p data/vectorstore
mkdir -p connectors
mkdir -p scripts

# 2. Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
# ... (all packages)

# 3. Create requirements.txt
```

**Files to create:**
1. `requirements.txt` - All Python dependencies
2. `.env.example` - Environment variables template
3. `.gitignore` - Ignore .env, data/, __pycache__, etc
4. `app/config.py` - Pydantic settings
5. `app/main.py` - FastAPI app initialization
6. `app/core/database.py` - SQLAlchemy setup
7. `app/core/security.py` - JWT + bcrypt functions
8. `app/models/database/user.py` - User model
9. `app/models/database/conversation.py` - Conversation model
10. `app/models/schemas/requests.py` - Pydantic request models
11. `app/models/schemas/responses.py` - Pydantic response models
12. `app/api/routes/auth.py` - Register/Login endpoints
13. `app/api/dependencies.py` - get_current_user dependency
14. `app/utils/logging.py` - Structured logging setup
15. `app/utils/exceptions.py` - Custom exceptions

**Verification:**
```bash
# Start server
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
# Expected: {"username": "test", "created_at": "..."}

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
# Expected: {"access_token": "eyJ...", "token_type": "bearer"}
```

---

### Phase 2: RAG Pipeline (Day 1 - Afternoon)

**Goal:** ChromaDB working with InfinitePay data, searchable embeddings

**Steps:**
1. Create `scripts/scrape_infinitepay.py`
   - Use requests + BeautifulSoup
   - Scrape 6 pages listed in challenge
   - Extract clean text (remove nav, footer, ads)
   - Save to `data/infinitepay_content.json`

2. Create `scripts/seed_vectorstore.py`
   - Load scraped content
   - Chunk text (400 chars, 50 overlap)
   - Generate embeddings (Anthropic)
   - Store in ChromaDB (`data/vectorstore/`)

3. Create `app/services/vector_store.py`
   - Initialize ChromaDB client
   - `search(query: str, top_k: int) -> list[dict]`
   - `add_documents(documents: list[dict])`

**Verification:**
```python
# Test RAG
from app.services.vector_store import VectorStore

vs = VectorStore()
results = vs.search("What are the Pix fees?", top_k=3)

print(results)
# Expected: [
#   {"text": "...", "score": 0.85, "metadata": {"page": "pix"}},
#   ...
# ]
```

---

### Phase 3: Agent Implementation (Day 2 - Morning)

**Goal:** All 4 agents working independently

**Steps:**

1. **Base Agent Class** (`app/core/agents/base.py`)
   ```python
   from abc import ABC, abstractmethod
   from anthropic import Anthropic

   class BaseAgent(ABC):
       def __init__(self, anthropic_client: Anthropic):
           self.client = anthropic_client

       @abstractmethod
       def process(self, message: str, context: dict) -> dict:
           pass
   ```

2. **Router Agent** (`app/core/agents/router.py`)
   - Use Claude with few-shot examples
   - Return: `{"target_agent": "knowledge", "confidence": 0.95}`
   - Test with 10 different messages

3. **Knowledge Agent** (`app/core/agents/knowledge.py`)
   - RAG search → Claude with context
   - Fallback to Tavily if no RAG results
   - Cache responses (1 hour TTL)
   - Test: "Qual a taxa do Pix?", "How does Pix work?"

4. **Support Agent** (`app/core/agents/support.py`)
   - Implement 4 tools (user_lookup, transaction_history, account_status, transfer_troubleshoot)
   - Use Claude with tool calling
   - Test: "Show my account status", "My transfer failed"

5. **Slack Agent** (`app/core/agents/slack.py`)
   - Mocked escalation (just logs)
   - Generate ticket ID
   - Test: "Talk to a human"

**Verification:**
```python
# Test each agent independently
from app.core.agents.router import RouterAgent
from app.core.agents.knowledge import KnowledgeAgent

router = RouterAgent(client)
result = router.process("What are the Pix fees?", {})
# Expected: {"target_agent": "knowledge", "confidence": 0.95}

knowledge = KnowledgeAgent(client, vector_store)
response = knowledge.process("What are the Pix fees?", {})
# Expected: "As taxas do Pix na InfinitePay são..."
```

---

### Phase 4: Orchestrator Integration (Day 2 - Afternoon)

**Goal:** `/chat` endpoint working end-to-end

**Steps:**

1. Create `app/core/orchestrator.py`
   ```python
   class AgentOrchestrator:
       def __init__(self, router, knowledge, support, slack):
           self.router = router
           self.agents = {
               "knowledge": knowledge,
               "support": support,
               "slack": slack
           }

       async def process_message(self, message: str, user_id: str) -> dict:
           # 1. Router decides
           routing = await self.router.process(message, {})

           # 2. Call target agent
           target_agent = self.agents[routing["target_agent"]]
           response = await target_agent.process(message, {"user_id": user_id})

           # 3. Save to database
           await self.save_conversation(user_id, message, response, routing["target_agent"])

           return {
               "response": response,
               "agent_used": routing["target_agent"],
               "confidence": routing["confidence"]
           }
   ```

2. Create `app/api/routes/chat.py`
   ```python
   @router.post("/chat", response_model=ChatResponse)
   async def chat_endpoint(
       request: ChatRequest,
       current_user: User = Depends(get_current_user),
       orchestrator: AgentOrchestrator = Depends(get_orchestrator)
   ):
       result = await orchestrator.process_message(
           message=request.message,
           user_id=str(current_user.id)
       )

       return ChatResponse(**result)
   ```

3. Add guardrails (`app/services/guardrails.py`)
   - Check for inappropriate content
   - Block if detected
   - Log blocked messages

**Verification:**
```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' \
  | jq -r '.access_token')

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the Pix fees?","user_id":"test"}'

# Expected:
# {
#   "response": "As taxas do Pix na InfinitePay são gratuitas para...",
#   "agent_used": "knowledge",
#   "confidence": 0.95
# }
```

---

### Phase 5: Testing (Day 3 - Morning)

**Goal:** >80% test coverage, all critical paths tested

**Unit Tests:**
- `tests/unit/test_agents.py` - Test each agent independently
- `tests/unit/test_tools.py` - Test support tools
- `tests/unit/test_security.py` - Test JWT encode/decode, password hashing

**Integration Tests:**
- `tests/integration/test_auth_flow.py` - Register → Login → Protected endpoint
- `tests/integration/test_chat_flow.py` - Full chat flow (router → agent → response)
- `tests/integration/test_agent_orchestration.py` - Multi-agent scenarios

**Run tests:**
```bash
pytest --cov=app --cov-report=html
# Expected: >80% coverage
```

---

### Phase 6: Docker & Deploy (Day 3 - Afternoon)

**Goal:** Docker working locally, ready for Render.com deploy

**Files to create:**

1. `Dockerfile` (multi-stage build)
   ```dockerfile
   FROM python:3.11-slim as builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   FROM python:3.11-slim
   WORKDIR /app
   COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. `docker-compose.yml`
   ```yaml
   version: '3.8'
   services:
     backend:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./data:/app/data
       env_file:
         - .env
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   ```

**Verification:**
```bash
# Build and run
docker-compose up --build

# Test
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**Deploy to Render.com:**
1. Create account on render.com
2. Connect GitHub repo
3. Create Web Service
4. Set environment variables in dashboard
5. Deploy!

---

### Phase 7: Telegram Bot (Day 3 - Evening - BONUS)

**Goal:** Telegram bot working, calling backend API

**Create `connectors/telegram_bot.py`:**
```python
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_message(update: Update, context):
    user_message = update.message.text
    user_id = str(update.effective_user.id)

    response = requests.post(
        f"{BACKEND_URL}/chat",
        json={"message": user_message, "user_id": user_id},
        headers={"Authorization": f"Bearer {get_bot_token()}"},
        timeout=30
    )

    if response.status_code == 200:
        await update.message.reply_text(response.json()["response"])
    else:
        await update.message.reply_text("Desculpe, tive um problema.")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.run_polling()
```

**Setup:**
1. Talk to @BotFather on Telegram
2. `/newbot` → Create bot → Get token
3. Add token to `.env`: `TELEGRAM_BOT_TOKEN=123456:ABC...`
4. Run: `python connectors/telegram_bot.py`
5. Test: Send message to bot

---

### Phase 8: Frontend (Day 4 - Optional)

**Goal:** Next.js frontend deployed on Vercel

**Create `cw_challenge_frontend/` (separate repo):**
```bash
npx create-next-app@latest cw_challenge_frontend --typescript --tailwind
cd cw_challenge_frontend
```

**Components:**
- `app/page.tsx` - Main chat interface
- `components/ChatBox.tsx` - Message input + display
- `components/ConversationHistory.tsx` - List of past conversations
- `lib/api.ts` - Backend API client

**Deploy:**
1. Push to GitHub
2. Connect to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.render.com`
4. Deploy!

---

## 🎯 Mocked Data (Personalization)

**IMPORTANT:** Include interviewer names in mocked data to show attention to detail!

```python
# app/core/tools/user_lookup.py

MOCKED_USERS = {
    "user123": {
        "name": "Leonardo Frizzo",      # ← INTERVIEWER!
        "email": "leonardo.frizzo@cloudwalk.io",
        "account_status": "active",
        "verification_level": "full",
        "role": "Head of Engineering"
    },
    "user456": {
        "name": "Luiz Silva",           # ← CEO!
        "email": "luiz.silva@cloudwalk.io",
        "account_status": "active",
        "verification_level": "full",
        "role": "CEO"
    },
    "user789": {
        "name": "Test User",
        "email": "test@example.com",
        "account_status": "active",
        "verification_level": "basic"
    }
}

def user_lookup(user_id: str) -> dict:
    return MOCKED_USERS.get(user_id, MOCKED_USERS["user789"])
```

**Why?** Shows you did research, care about details, and personalize the demo!

---

## 🚫 Common Pitfalls & How to Avoid

### 1. Router Agent Misclassifies
**Problem:** "What's the Pix fee?" goes to Support instead of Knowledge
**Solution:**
- Add more few-shot examples
- Include keywords list: `["fee", "price", "cost", "how much"] → KNOWLEDGE`

### 2. RAG Returns Irrelevant Results
**Problem:** Vector search returns wrong chunks
**Solution:**
- Smaller chunks (400 chars instead of 1000)
- More overlap (50 chars)
- Filter by score threshold (>0.7)
- Add metadata (page, section)

### 3. Agents Take Too Long
**Problem:** Request timeouts (>30s)
**Solution:**
- Use async/await properly
- Cache responses (1 hour TTL)
- Set Claude max_tokens=500 (faster)
- Use streaming if needed

### 4. Authentication Issues
**Problem:** JWT tokens invalid
**Solution:**
- Check SECRET_KEY is same across instances
- Verify token expiration (30 minutes)
- Test with: `jwt.io` decoder

### 5. Docker Volume Issues
**Problem:** SQLite database not persisting
**Solution:**
```yaml
# docker-compose.yml
volumes:
  - ./data:/app/data  # ← Make sure this is correct
```

---

## 📚 README.md Structure (Final Deliverable)

```markdown
# CloudWalk Agent Swarm Challenge

## Overview
[Brief description, architecture diagram, deployed links]

## Quick Start
```bash
# 1. Clone
git clone ...

# 2. Setup
cp .env.example .env
# Edit .env with your API keys

# 3. Run with Docker
docker-compose up

# 4. Test
curl http://localhost:8000/health
```

## Architecture
[Detailed explanation, diagrams, design decisions]

### Channel-Agnostic Design
[Explain pluggable connectors, Telegram vs WhatsApp decision]

## Agents
[Describe each agent, tools, decision logic]

## RAG Pipeline
[Explain ChromaDB, embeddings, chunking strategy]

## Authentication
[JWT flow, security measures]

## Testing
```bash
pytest --cov=app
```

## Deployment
[Render.com deploy instructions, env vars setup]

## Design Decisions
[Why monolith, why SQLite, why Telegram first, why JWT manual]

## Future Improvements
[What would be done differently in production]

## License
MIT
```

---

## ✅ Success Criteria Checklist

### Core Requirements
- ✅ Router Agent (classifies intent)
- ✅ Knowledge Agent (RAG + web search)
- ✅ Support Agent (4+ mocked tools)
- ✅ POST /chat endpoint (accepts message + user_id)
- ✅ Docker + docker-compose working
- ✅ Unit tests + integration tests
- ✅ Comprehensive README

### Bonus Features
- ✅ Slack Agent (4th agent - escalation)
- ✅ Guardrails (content moderation)
- ✅ JWT Authentication (manual implementation)
- ✅ Telegram Bot (channel-agnostic architecture)
- ✅ Conversation history (database + API)
- ✅ Deployed (Render.com + Vercel)

### Code Quality
- ✅ No inline comments (self-documenting)
- ✅ English-only code (PT-BR responses)
- ✅ Type hints everywhere
- ✅ SOLID principles
- ✅ Structured logging
- ✅ Security best practices

### Deliverables
- ✅ Backend deployed and accessible
- ✅ Frontend deployed (if time permits)
- ✅ Video demo (showing agents working)
- ✅ README explains everything
- ✅ Tests passing (>80% coverage)

---

## 🎥 Video Demo Script (5-10 minutes)

**Introduction (0:00-1:00)**
- "Hi Leonardo, I'm excited to show you my Agent Swarm implementation"
- "Built with FastAPI, LangChain, and Claude for CloudWalk's challenge"
- "Deployed and running at [URL]"

**Architecture Overview (1:00-2:30)**
- Show architecture diagram
- Explain Router → Knowledge/Support/Slack flow
- Mention channel-agnostic design (Telegram bot as bonus)

**Live Demo (2:30-6:00)**
1. **Swagger UI:** Show `/docs`, endpoints
2. **Knowledge Agent:** "What are the Pix fees?" → Shows RAG in action
3. **Support Agent:** "Show my account status" → Calls user_lookup tool
4. **Telegram Bot:** Send message via Telegram, get response
5. **Escalation:** "Talk to a human" → Slack agent generates ticket

**Code Walkthrough (6:00-8:00)**
- Router agent classification logic
- RAG pipeline (ChromaDB + embeddings)
- Tool calling in Support agent
- JWT authentication flow

**Design Decisions (8:00-9:30)**
- Why monolith (not microservices)
- Why SQLite (easy migration to PostgreSQL)
- Why Telegram first (official API, stable)
- Why JWT manual (demonstrates security skills)

**Conclusion (9:30-10:00)**
- "All tests passing, deployed, production-ready"
- "Thank you for the opportunity!"

---

## 🚀 Next Steps After Foundation

1. ✅ **Create directory structure**
2. ✅ **Write requirements.txt**
3. ✅ **Setup .env.example & .gitignore**
4. ✅ **Implement Phase 1** (FastAPI + Auth + Database)
5. ✅ **Implement Phase 2** (RAG Pipeline)
6. ✅ **Implement Phase 3** (Agents)
7. ✅ **Implement Phase 4** (Orchestrator + /chat)
8. ✅ **Implement Phase 5** (Tests)
9. ✅ **Implement Phase 6** (Docker + Deploy)
10. ✅ **Implement Phase 7** (Telegram Bot - Bonus)
11. ✅ **Implement Phase 8** (Frontend - Optional)
12. ✅ **Record video demo**
13. ✅ **Submit!**

---

## 📞 Contact & Support

**Developer:** [Your Name]
**Email:** [Your Email]
**LinkedIn:** [Your LinkedIn]
**GitHub:** [Your GitHub]

**Hiring Context:**
- **Company:** CloudWalk
- **CEO:** Luiz Silva
- **Interviewer:** Leonardo Frizzo
- **Position:** Senior Backend Engineer

---

## 🏁 Final Notes

This foundation document serves as the **single source of truth** for the entire project. Every decision, every file, every step is documented here.

**Remember:**
1. 🎯 **Quality over quantity** - 4 perfect agents > 10 mediocre ones
2. 🧹 **Clean code** - No comments, self-explanatory
3. 🔒 **Security first** - JWT, bcrypt, env vars
4. 📊 **Test everything** - >80% coverage
5. 📝 **Document decisions** - README explains "why"
6. 🚀 **Deploy early** - Find issues before deadline
7. 🎥 **Great demo** - Show, don't just tell

**This is for Leonardo Frizzo and CloudWalk. Make it 10/10!** 🔥

---

**Last Updated:** 2026-02-06
**Status:** Foundation Complete - Ready for Implementation
**Next:** Phase 1 - Project Setup
