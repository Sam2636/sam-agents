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

https://medium.com/@anuragmishra_27746/building-multi-agents-supervisor-system-from-scratch-with-langgraph-langsmith-b602e8c2c95d
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
        npm install react-router-dom


         uvicorn app:app --reload --port 8001
         .\venv\Scripts\activate
         npm i

zipping-- command
Compress-Archive -Path . -DestinationPath code.zip
