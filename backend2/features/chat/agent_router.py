"""
AgentRouter — wraps backend2's MultiAgent for use inside FastAPI.
Uses per-vector_id caching and runs blocking invoke() in a threadpool.
"""
import traceback
from starlette.concurrency import run_in_threadpool
from multi_agent import MultiAgent

_agent_cache: dict[str, MultiAgent] = {}


def _get_or_create_agent(vector_id: str) -> MultiAgent:
    if vector_id not in _agent_cache:
        _agent_cache[vector_id] = MultiAgent(vectorstore=vector_id)
    return _agent_cache[vector_id]


def _invoke_agent(vector_id: str, query: str) -> dict:
    try:
        agent = _get_or_create_agent(vector_id)
        result = agent.invoke(query)

        messages = result.get("messages", [])
        final_message = messages[-1] if messages else None

        agent_name = "Multi-Agent"
        for msg in reversed(messages):
            name = getattr(msg, "name", None) or (msg.get("name") if isinstance(msg, dict) else None)
            if name in ("diet_specialist", "discharge_specialist"):
                agent_name = name.replace("_", " ").title()
                break

        response_text = (
            final_message.content if hasattr(final_message, "content") else str(final_message)
        )
        return {"agent": agent_name, "response": response_text}

    except Exception:
        print("\n========== AGENT ERROR TRACEBACK ==========")
        traceback.print_exc()
        print("===========================================\n")
        raise


class AgentRouter:
    async def ask(self, vector_id: str, query: str) -> dict:
        return await run_in_threadpool(_invoke_agent, vector_id, query)
