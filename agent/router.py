from langgraph.graph import END
from agent.state import AgentState
from config.settings import AGENT_MAX_ITERATIONS

def should_continue(state: AgentState) -> str:
    """
    Decide o próximo passo após o LLM responder.
    Retorna o nome do próximo nó ou END.
    """
    last = state["messages"][-1]
    iters = state.get("iterations", 0)

    # proteção contra loop infinito
    if iters >= AGENT_MAX_ITERATIONS:
        return END

    # se o modelo pediu uma tool, executa
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"

    # resposta final — salva e encerra
    return "save_memory"

