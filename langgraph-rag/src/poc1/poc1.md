┌────────────────────────┐
│        React UI         │
│ (chat interface + stream│
│  token rendering)       │
└────────────┬───────────┘
             │  (HTTP / WS)
┌────────────┴───────────┐
│       FastAPI Layer     │
│  /chat  -> Normal mode  │
│  /chat-stream -> Stream │
│                        │
│ Uses LangChain Agent + │
│ MultiServerMCPClient   │
└────────────┬───────────┘
             │
┌────────────┴───────────┐
│     MCP Server Layer    │
│ (MySQL, etc.)           │
│  FastMCP / streamable   │
│  Custom DB Tools        │
└────────────┬───────────┘
             │
┌────────────┴───────────┐
│     MySQL Database      │
└────────────────────────┘


structure

poc1/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── agent.py            # LLM + MCP integration logic
│   ├── .env
│   └── requirements.txt
└── frontend/
    └── (your React app)
        npm create vite@latest frontend -- --template react

         uvicorn app:app --reload --port 8001
