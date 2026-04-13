from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    memory: dict # camada 1 sempre presente
    loaded_topics: list[str]  # camadas 2 carregadas no turno
    interations: int # proteção contra loops
    user_input: str # input bruto do turno atual
