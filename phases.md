# RideWise Assist - Execution Phases

The hackathon provides a 3-hour build window, but since we are short on time, this timeline is compressed to **1 hour**. It is broken down into 4 rapid phases.

## Phase 1: Foundation & RAG Setup (15 mins)
- Set up isolated project structures (`backend_service/` and `frontend_app/`).
- Initialize environment variables and install dependencies.
- Implement `LLMClient` to connect to the NeoStats-hosted model.
- Implement `KnowledgeBaseService` to ingest the 5 policy PDFs, chunk the text, and set up a local FAISS vector store for semantic search.

## Phase 2: Database & Access Control (15 mins)
- Implement `DatabaseService` with a read-only connection to `ridewise.db`.
- Implement `AccessControlManager` to handle role validation.
- Write logic to map a user's 10-digit Mobile Number to their `customer_id` using the `customers` table.
- Implement SQL validation checks to ensure customer queries are scoped to their specific `customer_id`.

## Phase 3: Agent Orchestration (15 mins)
- Implement the `AgentOrchestrator` in Python.
- Define JSON Schemas for two tools: `search_policies` and `query_database`.
- Write the native tool-calling loop: send query -> receive tool call request -> execute python function -> append raw data -> get final LLM response.
- Expose the orchestrator via a FastAPI `/api/chat` route.

## Phase 4: Frontend Development & Integration (15 mins)
- Scaffold the React/Vite application.
- Build the UI: Role dropdown, Mobile Number input, and the main Chat Window.
- Connect the frontend to the FastAPI `/api/chat` endpoint.
- Test the system end-to-end against edge cases (e.g., trying to access another user's booking).
- Finalize `README.md` and `DECISIONS.md` deliverables.
