# Task Checklist

## Setup
- [ ] Initialize Python environment (`backend_service`) and install dependencies (FastAPI, uvicorn, openai, faiss-cpu, sentence-transformers, python-dotenv).
- [ ] Set up `.env` and `.env.example` with LLM credentials.
- [ ] Initialize React environment (`frontend_app`) using Vite.

## Backend: Services
- [ ] **LLMClient:** Create wrapper for Azure OpenAI endpoint.
- [ ] **KnowledgeBaseService:**
  - [ ] Write PDF loader/parser.
  - [ ] Write text chunker.
  - [ ] Generate embeddings and build FAISS index.
  - [ ] Write similarity search function.
- [ ] **DatabaseService:**
  - [ ] Configure SQLite read-only connection.
  - [ ] Create function to safely execute SQL and return results.
- [ ] **AccessControlManager:**
  - [ ] Write `resolve_customer_id(mobile_number)` function.
  - [ ] Write logic to validate/enforce `customer_id` in SQL queries.

## Backend: Orchestration
- [ ] **AgentOrchestrator:**
  - [ ] Define system prompt with DB schema (`data_dictionary.md`).
  - [ ] Define `tools` schema for the LLM.
  - [ ] Implement the execution loop handling `tool_calls`.
- [ ] **API Endpoint:**
  - [ ] Create FastAPI app.
  - [ ] Add POST `/api/chat` endpoint that accepts `role`, `identifier`, and `message`.

## Frontend
- [ ] Create role selection UI (Customer / Support Agent).
- [ ] Create identifier input (Mobile Number / Customer ID).
- [ ] Create Chat message list UI.
- [ ] Create input box & send button.
- [ ] Write API client to call FastAPI backend and handle loading states.

## Final Review
- [ ] Test cross-customer data leakage (Ensure failure).
- [ ] Test policy questions (RAG).
- [ ] Write `README.md`.
- [ ] Write `DECISIONS.md`.
- [ ] Commit all changes to local Git repo.
