
"""
agent/graph.py
 
Monta e compila o grafo LangGraph do local-agent-kit.
"""

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from agent.state import AgentState
from agent.nodes import (
    node_load_memory,
    node_build_context,
    node_call_llm,
    node_save_memory,
)
from agent.router import should_continue
from tools.registry import get_tools

def build_graph() -> "CompiledGraph":
    """
    Constrói e compila o grafo do agente.
 
    Fluxo:
        load_memory → build_context → call_llm → [router]
                                                     ├── tools → call_llm (loop)
                                                     ├── save_memory → END
                                                     └── END (max iterations)
 
    Returns:
        CompiledGraph pronto para .invoke() ou .stream()
    """

    graph = StateGraph(AgentState)

    # Registra os nós
    graph.add_node("load_memory", node_load_memory)
    graph.add_node("build_context", node_build_context)
    graph.add_node("call_llm", node_call_llm)
    graph.add_node("save_memory", node_save_memory)

    # ponto de entrada
    graph.set_entry_point("load_memory")

    # Arestas fixas (sempre seguem esse caminho)
    graph.add_edge("load_memory", "build_context")
    graph.add_edge("build_context", "call_llm")
    graph.add_edge("save_memory", END)

    #Aresta condicional (router decide o próximo passo)
    graph.add_conditional_edges(
        "call_llm",
        should_continue,
        {
            "tools": "tools",
            "save_memory": "save_memory",
            END: END
        }
    )

    graph.add_edge("tools", "call_llm")

    return graph.compile()