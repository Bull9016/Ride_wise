# RideWise Assist - Ideation and Implementation Plan

## 1. Understanding the Requirements

**Goal:** Build "RideWise Assist", a conversational AI that answers queries for customers and support agents using a SQLite database (structured data) and 5 policy PDFs (unstructured data).

**Constraints & Rules:**
- 3 hours build time.
- Must use the provided NeoStats-hosted LLM (`gpt-oss-120b`).
- Must run locally with <10 mins setup time.
- No modifications to the provided DB or documents.
- Must evaluate to 100% accurate, honest, and verifiable answers without hallucination.

**User Personas & Security (Crucial):**
- **Customer:** Authenticates with `customer_id`. Can *only* access their own bookings, payments, and account info. Can access public policies.
- **Support Agent:** Can access all operational data (cross-customer) and all policies.

## 2. System Architecture

To ensure a highly modular, OOP-driven, and premium-feeling application within the time constraints, we will use a **strictly decoupled architecture** with **zero file sharing** between the frontend and backend.

- **Frontend:** React (using Vite). A standalone application responsible only for the UI, state management, and rendering. It communicates with the backend **exclusively via REST API calls over HTTP**.
- **Backend:** Python + FastAPI. A standalone service handling all business logic, LLM coordination, database access, and RAG. It exposes a clean REST API for the frontend to consume.
- **Strict Boundary:** No shared types, configuration files, environment variables, or helper functions between frontend and backend. They are treated as completely independent projects.
- **Data Layers:** 
  - **SQL DB:** `ridewise.db` (Read-only access).
  - **Vector DB:** Local vector store (e.g., FAISS or ChromaDB) using an open-source local embedding model (e.g., `all-MiniLM-L6-v2`) since no embedding model was explicitly provided in the wrapper.

## 3. Object-Oriented Design & Modularity

The backend will be structured into distinct, decoupled classes adhering to the Single Responsibility Principle (SRP).

### Core Classes & Modules:

1. **`LLMClient`**
   - **Responsibility:** Wrapper around the OpenAI API.
   - **Methods:** `generate_response(messages, tools)`, `get_embeddings(text)`

2. **`DatabaseService`**
   - **Responsibility:** Manages SQLite connections and executes queries safely.
   - **Methods:** `get_schema_info()`, `execute_query(sql_query)`
   - *Security detail:* Runs in read-only mode to prevent accidental data mutation.

3. **`KnowledgeBaseService` (RAG)**
   - **Responsibility:** Parses PDFs, chunks text, creates embeddings, and performs similarity search.
   - **Methods:** `ingest_documents(docs_path)`, `search(query, top_k)`

4. **`AccessControlManager`**
   - **Responsibility:** Enforces the strict data entitlement rules.
   - **Methods:** `validate_sql(query, role, customer_id)` 
   - *Security detail:* Intercepts Text-to-SQL outputs. If role is `Customer`, it ensures the SQL query explicitly filters by their `customer_id` and does not access cross-customer aggregates.

5. **`ToolRegistry`**
   - **Responsibility:** Defines and registers the tools available to the LLM (e.g., `query_database`, `search_policies`).

6. **`AgentOrchestrator`**
   - **Responsibility:** The core engine. It manages the conversation history, defines the available tools (functions), and leverages the LLM's **native tool calling** capabilities to dynamically decide whether to query the DB or search the PDFs.
   - **Methods:** `chat(user_input, role, customer_id)`

## 4. Execution Plan (Step-by-Step)

### Phase 1: Foundation & RAG Setup (45 mins)
- Set up project structure (`backend/`, `frontend/`).
- Implement `LLMClient` using the provided credentials.
- Implement `KnowledgeBaseService`: Parse the 5 PDFs, chunk them, embed using a lightweight local model (`sentence-transformers`), and store in a local FAISS index.

### Phase 2: Database & Text-to-SQL (45 mins)
- Implement `DatabaseService` to connect to `ridewise.db`.
- Extract DB schema strings from `data_dictionary.md` to feed into the LLM prompt.
- Implement `AccessControlManager`. For Text-to-SQL, we will inject a strict system prompt: *"You are querying a SQLite DB. The user is a customer with ID '{customer_id}'. EVERY query MUST include `WHERE customer_id = '{customer_id}'`."*

### Phase 3: Agent Orchestration (Native Tool Calling) (45 mins)
- **Why it's needed:** We have two disparate data sources (the SQL DB and the PDFs). When a user asks a question, the system must autonomously decide which source has the answer.
- **Implementation:** We will use the **Native Tool Calling (Function Calling)** capabilities of the LLM via the official OpenAI Python SDK.
- **Define Tools:** We will pass a `tools` array to the LLM containing JSON Schema definitions for our python functions:
  - `query_rental_policies(search_query)` -> Triggers `KnowledgeBaseService` (for unstructured RAG).
  - `query_operational_database(sql_query)` -> Triggers `AccessControlManager` then `DatabaseService` (for structured data).
- **The Orchestration Flow:** 
  1. Send user query + `tools` definitions to LLM.
  2. If the LLM responds with a `tool_calls` request, the Python backend executes the corresponding function.
  3. The raw results from the DB or FAISS are appended to the `messages` array as a `"role": "tool"` message.
  4. The LLM is called again to synthesize the final natural language answer.
- **Robustness:** If the SQL query fails (e.g., syntax error), the backend catches the exception and returns the error text as the tool response, allowing the LLM to self-correct its SQL and try again.

### Phase 4: API & Frontend (45 mins)
- Wrap the `AgentOrchestrator` in a FastAPI endpoint (`/api/chat`).
- Build a beautiful React/Vite UI with:
  - A role selector (Customer vs. Support Agent).
  - An input field for **Mobile Number** (or `customer_id`) if Customer is selected. This allows real users to identify themselves easily using their 10-digit phone number, while still allowing evaluators to use `customer_id` directly. The backend will automatically look up the `customer_id` from the `customers` table if a phone number is provided.
  - A modern, glass-morphism chat interface with typing indicators and markdown support for tables/lists.

## 5. Risk Mitigation & Security Strategies
- **Hallucinations:** We will use a low temperature (0.0) and prompt the LLM to strictly answer "I don't know" if the data is not in the search results or DB.
- **SQL Injection / Data Leakage:** Ensure the DB connection is read-only (`URI file:ridewise.db?mode=ro`). The `AccessControlManager` will parse the AST of the generated SQL to guarantee `customer_id` is present in the `WHERE` clause for customer roles before execution.

## 6. Engineering Standards & Git Workflow

To achieve maximum points for "Engineering Quality" and comply with Hackathon rules:
- **Strict Coding Conventions:** 
  - Python (Backend): Use strict type hinting (`-> dict`, `: str`), comprehensive docstrings for all classes/methods, and PEP-8 formatting (using Black/Ruff).
  - React (Frontend): Use functional components, hooks, clean prop-typing, and consistent formatting (Prettier/ESLint).
- **Environment Variables:** All secrets (like the Azure OpenAI API Key and endpoint) MUST be loaded from a `.env` file using `python-dotenv`. A `.env.example` file will be maintained and committed.
- **Git Strategy:** 
  - Initialize the Git repository immediately (`git init`).
  - Make frequent, atomic commits with clear, descriptive messages (e.g., `feat: implement ReAct orchestrator loop`). The commit history is explicitly evaluated.
  - Push the repository to GitHub before the 3-hour deadline.

## 7. Project Directory Structure

*(Note: The frontend and backend exist in their own isolated domains with separate dependency management and environments, sharing absolutely no files.)*

```
ridewise_assist/
├── backend_service/           # Completely isolated Python environment
│   ├── requirements.txt
│   ├── app.py                 # FastAPI entry point
│   ├── core/
│   │   ├── agent.py           # AgentOrchestrator
│   │   ├── llm.py             # LLMClient
│   │   └── security.py        # AccessControlManager
│   ├── services/
│   │   ├── database.py        # DatabaseService
│   │   └── knowledge.py       # KnowledgeBaseService
│   └── data/
│       ├── ridewise.db
│       └── vector_store/
│
├── frontend_app/              # Completely isolated Node/React environment
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── components/
│   │   ├── api/               # API clients to make HTTP calls to backend
│   │   └── App.jsx
│
├── README.md
└── DECISIONS.md
```
