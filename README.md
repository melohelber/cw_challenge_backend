# CloudWalk Agent Swarm Challenge

**Agent Swarm System for InfinitePay Customer Support**

## 🎯 Overview

Production-ready multi-agent system built with FastAPI, LangChain, and Claude AI for intelligent customer support. Features RAG (Retrieval-Augmented Generation), tool calling, and automatic escalation.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# - ANTHROPIC_API_KEY (get from https://console.anthropic.com/)
# - TAVILY_API_KEY (get from https://tavily.com/)
# - SECRET_KEY (generate with: openssl rand -hex 32)
```

### 2. Run with Docker

```bash
# Build and start
docker compose up --build

# Or run in background
docker compose up -d
```

### 3. Test the API

```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

---

## 🏗️ Architecture

```
User Message
    ↓
Guardrails (content moderation)
    ↓
Router Agent (classifies intent)
    ↓
┌─────────────┬──────────────┬───────────────┐
│  Knowledge  │   Support    │    General    │
│   Agent     │    Agent     │     Agent     │
│ (RAG+Web)   │   (Tools)    │  (Fallback)   │
└─────────────┴──────────────┴───────────────┘
    ↓ (if agent fails)
Slack Agent (escalation)
```

### Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| **Router** | Classifies user intent into KNOWLEDGE, SUPPORT, or GENERAL | - |
| **Knowledge** | Answers questions using RAG (InfinitePay docs) + web search | ChromaDB, Tavily API |
| **Support** | Handles account-specific requests | 4 mocked tools (see below) |
| **Slack** | Escalates to human support when agents fail | Mocked (logs only) |

### Knowledge Agent - Intelligent Routing & Fallback

The Knowledge Agent uses a **single source of truth architecture** where the Router's AI classification determines the data source:

```
Router AI Decision
    ↓
┌─────────────────────────────────────────┐
│ KNOWLEDGE (InfinitePay-related)         │
│   → Try RAG (ChromaDB search)           │
│       ├─ Found documents? → Use RAG     │
│       └─ Empty results? → Fallback to   │
│          Tavily web search              │
└─────────────────────────────────────────┘
         OR
┌─────────────────────────────────────────┐
│ GENERAL (Off-topic)                     │
│   → Use Tavily web search directly      │
└─────────────────────────────────────────┘
```

**Key Benefits:**
- ✅ **Single AI Classification** - Router decides once, Knowledge Agent trusts it
- ✅ **Automatic Fallback** - If RAG doesn't find InfinitePay docs, uses web search
- ✅ **No Hardcoded Keywords** - AI-based classification instead of keyword matching
- ✅ **Always Returns Context** - Never leaves user without an answer

**Example Flow:**

```bash
# Scenario 1: InfinitePay question WITH docs in RAG
User: "Qual a taxa do Pix?"
Router: KNOWLEDGE → Knowledge Agent → RAG finds docs → Returns InfinitePay info

# Scenario 2: InfinitePay question WITHOUT docs in RAG
User: "Como funciona adquirente na InfinitePay?"
Router: KNOWLEDGE → Knowledge Agent → RAG empty → Fallback to Tavily → Web search

# Scenario 3: General question
User: "What's the weather today?"
Router: GENERAL → Knowledge Agent → Tavily web search directly
```

**Conversational Messages:**
Simple greetings like "Oi", "Tudo bem?" skip web search entirely and let the AI respond naturally, saving Tavily API credits.

---

## 🛠️ Support Agent Tools (Mocked)

The Support Agent has access to 4 tools that simulate real backend services:

### 1. User Lookup
Retrieves user profile information.

### 2. Transaction History
Returns recent transactions for a user.

### 3. Account Status
Checks account limits, restrictions, and daily usage.

### 4. Transfer Troubleshoot
Diagnoses transfer issues given a transfer_id.

### 🎭 Mock Data

#### Personalized User IDs (for demo):
- `"user_leo"` - **Leonardo Frizzo** (Head of Engineering)
- `"user_luiz"` - **Luiz Silva** (CEO)
- `"user_test"` - Maria Santos (default test user)
- `"user_blocked"` - João Silva (blocked account demo)

#### Fallback Behavior:
For **any other user_id** (e.g., numeric IDs like "1", "2", "3"), the tools automatically use the `"user_test"` mock data as fallback. This ensures the system works for all users without manual setup.

**Example:**
```bash
# User logs in with user_id "2"
# Support tools automatically return:
# - Name: Maria Santos
# - Transactions: 2 recent payments
# - Account status: Active
```

#### Test Commands:
```bash
# Login as user "2"
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Get token, then test Support Agent:
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Show my recent transactions"}'

# Expected: Returns 2 transactions (Padaria + Uber)
```

---

## 🔑 Authentication

- **JWT-based** authentication (manual implementation)
- Tokens expire after **30 minutes**
- Protected endpoints: `/chat`, `/history`
- Public endpoints: `/auth/register`, `/auth/login`

### Register & Login

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secret123"}'

# Returns: {"access_token": "eyJ...", "token_type": "bearer"}
```

---

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Create new user
- `POST /auth/login` - Get JWT token

### Chat (Protected)
- `POST /chat` - Send message to agent system
  - Request: `{"message": "Your question here"}`
  - Response: `{"response": "Agent answer", "agent_used": "knowledge", "confidence": "high"}`

### Health
- `GET /health` - Health check
- `GET /` - API info

---

## 🧪 Testing with Postman

Import the provided Postman collection:

```bash
# File: CloudWalk_Agent_Swarm.postman_collection.json
```

**Features:**
- ✅ Auto JWT refresh (pre-request script)
- ✅ Pre-configured test requests
- ✅ Knowledge, Support, and Guardrails examples

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
TAVILY_API_KEY=tvly-your-key-here
SECRET_KEY=your-secret-key-min-32-chars

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./data/app.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Claude Models (2026)

Available models in `.env`:
```bash
# Fastest (recommended for testing)
ANTHROPIC_MODEL=claude-haiku-4-5-20251001

# Balanced (best performance/cost)
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Smartest (premium)
ANTHROPIC_MODEL=claude-opus-4-6
```

---

## 📊 Project Structure

```
cw_challenge_backend/
├── app/
│   ├── api/                 # API routes & dependencies
│   │   ├── routes/
│   │   │   ├── auth.py      # Register/Login
│   │   │   └── chat.py      # Main chat endpoint
│   │   └── dependencies.py  # JWT validation
│   ├── core/
│   │   ├── agents/          # AI Agents
│   │   │   ├── router.py
│   │   │   ├── knowledge.py
│   │   │   ├── support.py
│   │   │   └── slack.py
│   │   ├── tools/           # Support tools (mocked)
│   │   │   ├── user_lookup.py
│   │   │   ├── transaction_history.py
│   │   │   ├── account_status.py
│   │   │   └── transfer_troubleshoot.py
│   │   ├── orchestrator.py  # Agent coordinator
│   │   ├── database.py
│   │   └── security.py      # JWT + bcrypt
│   ├── services/            # External services
│   │   ├── vector_store.py  # ChromaDB (RAG)
│   │   ├── guardrails.py    # Content moderation
│   │   └── web_search.py    # Tavily integration
│   ├── models/
│   │   ├── database/        # SQLAlchemy ORM
│   │   └── schemas/         # Pydantic models
│   ├── utils/
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── config.py            # Settings (Pydantic)
│   └── main.py              # FastAPI app
├── tests/
│   ├── unit/
│   └── integration/
├── data/                    # SQLite DB + vector store
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🧩 Key Features

✅ **Multi-Agent System** - Router → Knowledge/Support/Slack
✅ **RAG (Retrieval-Augmented Generation)** - ChromaDB + InfinitePay docs
✅ **Tool Calling** - Support Agent uses 4 mocked backend tools
✅ **Auto Escalation** - Failed agents → Slack Agent (ticket creation)
✅ **JWT Authentication** - Secure, token-based auth
✅ **Guardrails** - Content moderation for inappropriate requests
✅ **Conversation History** - SQLite database storage
✅ **Docker Ready** - One command deployment
✅ **Postman Collection** - Auto JWT + test requests

---

## 🎯 Example Conversations

### Knowledge Agent (RAG)
```
User: "What are the fees for the InfinitePay card machine?"
Agent: "Based on InfinitePay documentation:
- Debit: 0.75%
- Credit: 2.69%
- Pix: Zero fees"
```

### Support Agent (Tools)
```
User: "Show my recent transactions"
Agent: [Calls transaction_history tool]
"Here are your last 2 transactions:
1. Padaria São Paulo - R$ 150.00 (1 day ago)
2. Uber - R$ 50.00 (2 days ago)"
```

### Escalation (Slack Agent)
```
User: "I need to speak with a human"
Agent: "Your request has been escalated to our support team.
Ticket ID: SUP-20260206-123456
Estimated response: 15 minutes"
```

---

## 📚 Documentation

- **FOUNDATION.md** - Complete project specification
- **SETUP.md** - Detailed setup instructions
- **Postman Collection** - API testing guide

---

## 🔒 Security Best Practices

✅ Passwords hashed with bcrypt (cost=12)
✅ JWT tokens expire (30 min)
✅ API keys in `.env` (never committed)
✅ Input validation (Pydantic)
✅ CORS configured
✅ SQL injection protection (SQLAlchemy ORM)
✅ Sensitive data masked in logs

---

## 🚀 Deployment

### Local Development
```bash
docker compose up
```

### Production (Render.com)
1. Create Web Service
2. Connect GitHub repo
3. Set environment variables
4. Deploy!

---

## 👥 Contributors

**Developer:** [Your Name]
**Challenge:** CloudWalk Agent Swarm
**Interviewer:** Leonardo Frizzo (Head of Engineering)
**CEO:** Luiz Silva

---

## 📄 License

MIT

---

**Built with ❤️ for CloudWalk** 🚀
