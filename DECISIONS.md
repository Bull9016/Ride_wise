# Design Decisions (DECISIONS.md)

### 1. What were your three most important design decisions, and why?
* **Zero-Trust SQL Ast Execution:** Instead of letting the LLM generate unrestricted SQL, I built an `AccessControlManager` layer. For Customers, it physically intercepts the LLM's SQL string and enforces a `WHERE customer_id` check before executing against the SQLite DB. This ensures cross-customer data leakage is impossible at the database level, even if the LLM hallucinates or gets jailbroken.
* **Separation of Personas via System Prompt:** I separated the 'Customer' and 'Support Agent' logic directly within `agent.py`. The Customer gets heavily restricted instructions. The Support Agent gets access to everything, but with an explicit "In-Chat 2FA" constraint requiring them to provide a phone number to verify any data query. This makes the LLM behave accurately to its context.
* **Backend Sliding-Window SQLite Memory:** Instead of sending the entire chat history back and forth from the React frontend (which eats tokens and poses a security risk), I built a stateful `MemoryService` using a new `chat_state.db` SQLite file. The backend tracks conversations via a `session_id` UUID and only feeds the last 3 exchanges (6 messages limit) to the LLM.

### 2. Which alternatives did you consider and reject?
* **Relying purely on LLM guardrails for data access:** I rejected this because LLMs can be manipulated (prompt injection). Real data security must happen at the code execution layer, which is why I implemented the strict SQL interceptor in `security.py`.
* **Using an external managed vector database (like Pinecone) for RAG:** The rules restrict using other APIs, and I wanted to ensure the app runs completely locally and instantly for the judges. I opted for local FAISS indices and `HuggingFaceEmbeddings(all-MiniLM-L6-v2)`.
* **React Markdown Parsing via Raw HTML:** I initially tried basic markdown rendering in React, but complex LLM output (tables, lists) broke the DOM. I rejected simple parsers and implemented `marked` to safely render tables.

### 3. Where does your assistant currently fail or behave poorly?
* **Policy Version Conflicts:** The FAISS index chunks both `v1` and `v2` of the Cancellation Policies. While the LLM is instructed to prefer `v2`, semantic search will often surface highly relevant but outdated `v1` chunks. A true production system would either archive `v1` or implement metadata filtering in FAISS to prioritize newer documents natively.
* **Unoptimized Token Usage on SQL Schema:** The entire database schema (tables and columns) is injected into the System Prompt for every turn. As the database grows, this will become incredibly token-heavy.
* **SQL Error Feedback Loops:** If the LLM writes a syntax error in its SQL query, the `AccessControlManager` catches it and returns the error string to the LLM, but the LLM sometimes struggles to self-correct complex queries without human intervention.

### 4. What would you build next with one more week?
* **Dynamic Schema Fetching:** Instead of hardcoding the DB schema into the prompt, I would build a third tool (`describe_table`) so the LLM can explore the database structure dynamically, saving tokens.
* **Metadata Filtering in FAISS:** I would parse the document names/dates during ingestion and attach them as FAISS metadata, allowing the LLM to execute filtered semantic searches (e.g., `search_policies(query="refund", version="v2")`).
* **Semantic Routing for SQL:** Currently, all data requests go through text-to-SQL. For common questions ("What are my rides?"), I would implement hardcoded API routes that bypass the LLM entirely, only falling back to text-to-SQL for edge cases.
