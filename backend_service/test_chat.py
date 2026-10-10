import asyncio
import traceback
from core.agent import AgentOrchestrator
from services.database import DatabaseService
from services.knowledge import KnowledgeBaseService

db_service = DatabaseService()
kb_service = KnowledgeBaseService()
kb_service.vector_store_path = "data/faiss_index"
orchestrator = AgentOrchestrator(db_service, kb_service)

try:
    print("Testing chat with LLM...")
    ans = orchestrator.chat(
        user_message="Hello, what is the policy for late returns?",
        role="Support Agent",
        mobile_number=None,
        customer_id=None,
        history=[]
    )
    print("Answer:", ans)
except Exception as e:
    traceback.print_exc()
