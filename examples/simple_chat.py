"""
local-agent-kit — exemplo básico
Execute: python examples/simple_chat.py
"""
from langchain_core.messages import HumanMessage
from agent.graph import build_graph

def main():
    graph = build_graph()
    print("Agente local pronto. Digite 'sair' para encerrar.\n")

    while True:
        user_input = input("Você: ").strip()
        if user_input.lower() in ["sair", "exit", "quit"]:
            break
        if not user_input:
            continue

        result = graph.invoke({
            "messages":      [HumanMessage(content=user_input)],
            "memory":        {},
            "loaded_topics": [],
            "iterations":    0,
            "user_input":    user_input,
        })

        last = result["messages"][-1]
        print(f"\nAgente: {last.content}\n")

if __name__ == "__main__":
    main()