# RideWise Assist - System Architecture

## 1. High-Level Design
The system uses a strictly decoupled architecture with zero file sharing between the frontend and backend. They communicate exclusively via REST API over HTTP.

## 2. Frontend App (`frontend_app/`)
- **Tech Stack:** React, Vite, TailwindCSS (optional for speed).
- **Responsibility:** Handles the user interface, state management, and rendering of the chat.
- **Key Features:**
  - Role Selector (Customer vs. Support Agent).
  - Identifier Input (Accepts 10-digit Mobile Number or `customer_id`).
  - Modern Chat Interface with typing indicators and Markdown support.

## 3. Backend Service (`backend_service/`)
- **Tech Stack:** Python, FastAPI, OpenAI SDK, FAISS, SQLite3.
- **Responsibility:** Handles all business logic, LLM coordination, data retrieval, and security.

### Core Modules (OOP Design)
1. **`LLMClient`**: Wrapper around the Azure OpenAI SDK for `gpt-oss-120b`.
2. **`DatabaseService`**: Manages SQLite connections to `ridewise.db` in **Read-Only Mode** (`?mode=ro`).
3. **`KnowledgeBaseService` (RAG)**: Loads the 5 PDFs, chunks them, generates embeddings, and queries a local FAISS index.
4. **`AccessControlManager`**: Enforces entitlements. Resolves mobile numbers to `customer_id`. Validates that Text-to-SQL queries are strictly filtered by the authenticated `customer_id`.
5. **`AgentOrchestrator`**: The core LLM controller. Exposes `DatabaseService` and `KnowledgeBaseService` to the LLM via **Native Tool Calling (Function Calling)**. Manages the conversation history loop.

## 4. Security & Privacy
- **Customer Entitlement:** Customers can only query their own data. Text-to-SQL is strictly guarded.
- **Agent Entitlement:** Support Agents have cross-customer operational access.
- **Data Integrity:** Database is read-only.
- **Secrets:** Handled via `.env`.
