"""Supervisor Agent node for the LangGraph pipeline.

Parses operator intent into a structured TaskPlan using an LLM,
and routes to the appropriate sub-agent based on the first pending task.
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from src.core.state import AgentState, TaskPlan, TaskType

SUPERVISOR_SYSTEM_PROMPT = """\
You are the Supervisor of a Multi-Agent Orchestrator for a Software-Defined \
Optical Network (SDON) testbed. Your job is to:

1. Parse the operator's natural language intent.
2. Classify it into one or more tasks from the following types:
   - topology_query: Fetch or display current network topology.
   - route_request: Find an optical path between two nodes.
   - lightpath_provision: Create/configure a lightpath or service.
   - measurement: Start/query OSNR or power measurements.
   - unknown: Intent cannot be classified.
3. Return a structured TaskPlan with an intent_summary and ordered task list.

The testbed has 4 nodes: Milano-A, Milano-B, Milano-C, Milano-D in a linear \
topology. When the operator asks about the network state, topology, or \
connected nodes, classify it as topology_query.

Always respond with a valid TaskPlan JSON structure.\
"""

# Module-level LLM reference, set during graph initialization.
_llm: BaseChatModel | None = None


def set_supervisor_llm(llm: BaseChatModel) -> None:
    """Configure the LLM used by the supervisor node."""
    global _llm  # noqa: PLW0603
    _llm = llm


def get_supervisor_llm() -> BaseChatModel:
    """Retrieve the configured LLM or raise if not set."""
    if _llm is None:
        msg = (
            "Supervisor LLM not configured. "
            "Call set_supervisor_llm() before using supervisor_node."
        )
        raise RuntimeError(msg)
    return _llm


def create_default_llm(
    *,
    api_key: str,
    base_url: str | None = None,
    model: str = "kimi-k2-0711-preview",
) -> ChatOpenAI:
    """Create a ChatOpenAI instance configured for the Kimi API.

    Args:
        api_key: API key for the Kimi service.
        base_url: Custom base URL (required for Kimi).
        model: Model identifier to use.

    Returns:
        A configured ChatOpenAI instance.
    """
    kwargs: dict = {
        "model": model,
        "api_key": api_key,
        "temperature": 1,
        "max_tokens": 1500,
        "default_headers": {"User-Agent": "claude-code/0.2.9"},
    }
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


def supervisor_node(state: AgentState) -> dict:
    """Parse operator intent and create a task plan.

    Uses the LLM with structured output to produce a TaskPlan.
    On the first invocation (no task_plan), parses the intent.
    On subsequent invocations (task_plan exists), synthesizes the final response.

    Returns:
        Partial state update with task_plan, messages, and current_agent.
    """
    llm = get_supervisor_llm()

    # If we already have a task_plan AND topology data, synthesize response
    if state.get("task_plan") and state.get("topology_snapshot"):
        return _synthesize_response(state)

    # First pass: parse intent
    structured_llm = llm.with_structured_output(TaskPlan, method="json_mode")

    user_messages = [
        msg
        for msg in state["messages"]
        if isinstance(msg, dict) and msg.get("role") == "user"
        or hasattr(msg, "type") and msg.type == "human"
    ]

    if not user_messages:
        return {
            "messages": [
                AIMessage(
                    content="No operator message received. Awaiting input.",
                    name="supervisor",
                )
            ],
            "current_agent": None,
        }

    messages = [SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT)] + state["messages"]
    task_plan = structured_llm.invoke(messages)

    summary = (
        f"Intent parsed: {task_plan.intent_summary}. "
        f"Delegating {len(task_plan.tasks)} task(s)."
    )

    return {
        "task_plan": task_plan,
        "messages": [AIMessage(content=summary, name="supervisor")],
        "current_agent": "supervisor",
    }


def route_by_task(state: AgentState) -> str:
    """Conditional edge: route to the appropriate agent based on task type.

    Returns:
        The node name to route to, or "__end__" if no tasks remain.
    """
    task_plan = state.get("task_plan")
    if not task_plan or not task_plan.tasks:
        return "__end__"

    # If we already have topology data, we're done — synthesize
    if state.get("topology_snapshot"):
        return "__end__"

    first_task = task_plan.tasks[0]

    routing_map = {
        TaskType.TOPOLOGY_QUERY: "topology_agent",
        TaskType.ROUTE_REQUEST: "__end__",  # Not implemented yet
        TaskType.LIGHTPATH_PROVISION: "__end__",  # Not implemented yet
        TaskType.MEASUREMENT: "__end__",  # Not implemented yet
        TaskType.UNKNOWN: "__end__",
    }

    return routing_map.get(first_task.task_type, "__end__")


def _synthesize_response(state: AgentState) -> dict:
    """Generate a human-readable response from the completed state."""
    llm = get_supervisor_llm()
    topology = state["topology_snapshot"]

    prompt = (
        f"The topology agent has fetched the following network data:\n"
        f"Nodes: {[n.name for n in topology.nodes]}\n"
        f"Links: {[(l.source_node, l.target_node, f'{l.length_km}km') for l in topology.links]}\n"
        f"Active channels per link: {[l.active_channels for l in topology.links]}\n\n"
        f"Please provide a clear, concise summary of the network topology "
        f"for the operator. Include node names, connections, fiber lengths, "
        f"and amplifier counts."
    )

    response = llm.invoke([
        SystemMessage(
            content="You are the Supervisor of a Multi-Agent Orchestrator for a Software-Defined Optical Network (SDON) testbed. Summarize the topology data for the operator in a clear, friendly, and professional way."
        ),
        HumanMessage(content=prompt),
    ])

    return {
        "messages": [AIMessage(content=response.content, name="supervisor")],
        "current_agent": None,
    }
