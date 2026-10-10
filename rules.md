# RideWise Assist - Rules & Engineering Standards

## 1. Hackathon Constraints (Strictly Enforced)
- **Time Limit:** 3 hours.
- **LLM Usage:** Only use the NeoStats-hosted LLM (`gpt-oss-120b`). No personal API keys or local models.
- **Data Integrity:** The provided `ridewise.db` and the 5 policy PDFs MUST remain unmodified.
- **Pre-built Code:** Using pre-built solutions or project code written before the event is forbidden.
- **Hard-coding:** Hard-coding answers is prohibited. The system must adapt to unseen data/questions.

## 2. Engineering Quality (10% of Score)
- **Backend (Python):**
  - Use strict type hinting (`def get_data(customer_id: str) -> dict:`).
  - Include docstrings for all classes and major functions.
  - Adhere to PEP-8 formatting.
  - Follow Object-Oriented Programming (OOP) and Single Responsibility Principle (SRP).
- **Frontend (React):**
  - Use modern functional components and hooks.
  - Ensure clear prop-typing and state management.
- **Secrets Management:**
  - Never hardcode the Azure OpenAI API Key.
  - Load via `python-dotenv`.
  - Maintain a `.env.example` file in the repo.

## 3. Git Workflow
- Make frequent, atomic commits. The commit history is evaluated.
- Use descriptive commit messages (e.g., `feat: setup fastAPI route`, `fix: correct FAISS embedding bug`).
- The last commit before the deadline is treated as final.

## 4. Evaluation Criteria Checklist
When building, continually verify against these metrics:
1. **Correctness (30%):** Does the system extract the exact data from the DB and PDFs?
2. **Trust & Safety (15%):** Is it impossible for a customer to see another customer's data?
3. **Conversational Quality (15%):** Are responses natural and coherent?
4. **Adaptability (10%):** Can the system handle edge cases and slow model response times gracefully?
5. **Transparency (10%):** Is it clear where the assistant got its answer?
6. **Engineering Quality (10%):** Is the code clean, modular, and well-documented?
