from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

class AgentState(TypedDict):
    # Conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_query: str
    session_id: str

    # Routing
    current_agent: str
    next_agent: Optional[str]
    agent_sequence: list[str]

    # Agent outputs
    requirements: Optional[dict]
    plan: Optional[dict]
    generated_code: Optional[str]
    fixed_code: Optional[str]
    documentation: Optional[str]
    test_cases: Optional[str]
    deployment_config: Optional[str]

    # RAG context
    retrieved_context: Optional[str]

    # Control
    iteration_count: int
    max_iterations: int
    is_complete: bool
    error: Optional[str]