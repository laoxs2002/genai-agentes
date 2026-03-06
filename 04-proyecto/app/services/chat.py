"""
Invoke supervisor with thread_id (conversation_id) and optional context (user_id for long-term store).
When user_id is present, we inject it into the conversation so the agent can use guardar_preferencia.
"""
from __future__ import annotations

from fastapi import Request
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.supervisor import Context


def invoke_supervisor(
    request: Request,
    conversation_id: str,
    content: str,
    user_id: str | None = None,
) -> dict:
    """
    Invoke the supervisor agent. Returns the last assistant message content and whether a ticket was created.
    When user_id is set, the agent is told the current user_id so it can call guardar_preferencia.
    """
    supervisor = request.app.state.supervisor
    config = {"configurable": {"thread_id": conversation_id}}
    messages = []

    if user_id:
        # So the agent knows which user_id to pass to guardar_preferencia
        messages.append(
            SystemMessage(
                content=(
                    f"El identificador del usuario con el que hablas es: {user_id}. "
                    "Cuando el usuario pida guardar una preferencia (producto favorito, gustos, etc.), "
                    "usa la herramienta guardar_preferencia pasando este user_id como primer argumento."
                )
            )
        )
    messages.append(HumanMessage(content=content))
    context = Context(user_id=user_id) if user_id else None

    if context is not None:
        result = supervisor.invoke(
            {"messages": messages},
            config=config,
            context=context,
        )
    else:
        result = supervisor.invoke({"messages": messages}, config=config)

    msgs = result.get("messages", [])
    last_content = msgs[-1].content if msgs else ""

    # Detect if crear_ticket was called (simplified: check last tool_calls in result)
    ticket_created = False
    for m in reversed(msgs):
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                if isinstance(tc, dict) and tc.get("name") == "crear_ticket":
                    ticket_created = True
                    break
                if getattr(tc, "name", None) == "crear_ticket":
                    ticket_created = True
                    break
        if ticket_created:
            break

    return {"content": last_content, "ticket_created": ticket_created}
