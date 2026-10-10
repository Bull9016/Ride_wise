# Working Memory & Key Decisions

## Current State
- Ideation and Planning phase is complete.
- Local Git repository is initialized and first commit is made.
- GitHub push is blocked (Permission Denied 403) - will rely on local commits for now.

## Key Technical Decisions
1. **Tool Calling Strategy:** The system uses Native Tool Calling via the OpenAI SDK. If the open-source model (`gpt-oss-120b`) struggles with native JSON schemas, we will pivot to a manual ReAct loop.
2. **Strict Decoupling:** The `frontend_app` and `backend_service` are treated as completely independent projects. No shared files.
3. **Database Security:** `ridewise.db` is connected via `URI file:ridewise.db?mode=ro` (read-only) to completely prevent SQL injection from modifying or dropping tables.
4. **User Identification:** To make the app realistic, the frontend accepts a 10-digit mobile number. The backend maps this to a `customer_id` via a SQL lookup before starting the LLM orchestration.
5. **RAG Tooling:** We will use a lightweight local embedding model (like `sentence-transformers/all-MiniLM-L6-v2`) and FAISS, since no explicit embedding model was provided by the hackathon.

## Important File Locations
- Database: `ridewise.db`
- Data Dictionary: `data_dictionary.md`
- PDFs (Policies): `01_Rental_Agreement_and_Terms.pdf`, `02_...`, `03_...`, `04_...`, `05_...`
- LLM Wrapper: `sample_open_ai_wrapper.py`
