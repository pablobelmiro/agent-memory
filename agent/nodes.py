from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config.settings import * 
from memory.manager import MemoryManager
from tools.registry import get_tools
from agent.state import AgentState
from agent.prompts import build_system_prompt

mem = MemoryManager()

def get_llm():
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url= OLLAMA_BASE_URL,
        temperature=LLM_TEMPERATURE,
        num_predict=LLM_NUM_PREDICT,
        num_ctx=LLM_NUM_CTX,
        num_thread=LLM_NUM_THREAD
    )

def node_load_memory(state: AgentState) -> dict:
     """Carrega camada 1 (sempre) e decide quais tópicos carregar."""
     core = mem.load_core()
     topics = mem.load_relevant_topics(state["user_input"])
     return {
        "memory": core,
        "loaded_topics": topics
     }

def node_build_context(state: AgentState) -> dict:
    """Monta system prompt com memória injetada e trim do histórico."""
    system_content = build_system_prompt(
        core=state["memory"],
        topics=state["loaded_topics"]
    )

    system = SystemMessage(content=system_content)

    # mantém só os últimos N turnos
    non_system = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
    trimmed = non_system[-(AGENT_MAX_HISTORY_TURNS * 2):]

    return {
        "messages": [system] + trimmed
    }

def node_call_llm(state: AgentState) -> dict:
    """Chama o modelo local com as tools disponíveis."""
    llm = get_llm()
    tools = get_tools()
    chain = llm.bind_tools(tools) if tools else llm

    response = chain.invoke(state["messages"])

    return {
        "messages": [respose],
        "interations": state.get("iterations", 0) + 1
    }

def node_save_memory(state: AgentState) -> dict:
    """Extrai fatos do turno e persiste na memória."""
    last = state["messages"][-1]
    content = getattr(last, "content", "") or ""

    mem.extract_and_save(
        user_text=state["user_input"],
        assistant_text=content
    )
    mem.append(role="user", content=state["user_input"])
    mem.append(role="assistant", content=content)

    return {}

