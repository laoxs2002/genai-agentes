"""
Supervisor agent: create_agent with PostgresSaver, PostgresStore, RAG, Tavily, crear_ticket, subagentes.
"""
from pydantic import BaseModel

from langchain.agents import create_agent

from app.agents.tools import (
    make_buscar_documentacion_tool,
    make_tavily_tool,
    crear_ticket,
    guardar_preferencia,
)
from app.agents.subagents import make_invocar_tecnico_tool, make_invocar_comercial_tool
from app.core.config import get_settings


class Context(BaseModel):
    """Runtime context for long-term store (user_id)."""
    user_id: str


def build_supervisor(checkpointer, store):
    """Build the supervisor agent with checkpointer and store (from app lifespan)."""
    settings = get_settings()
    tools = [
        make_buscar_documentacion_tool(),
        make_tavily_tool(),
        crear_ticket,
        guardar_preferencia,
        make_invocar_tecnico_tool(),
        make_invocar_comercial_tool(),
    ]
    system_prompt = (
        "Eres un asistente de soporte al cliente. Coordina y delega: "
        "para dudas técnicas (especificaciones, códigos de error) usa soporte_tecnico; "
        "para precios, garantías y condiciones comerciales usa soporte_comercial. "
        "Para preguntas sobre documentación interna (manuales, políticas) usa buscar_documentacion. "
        "Para noticias o información actual en internet usa la búsqueda web. "
        "Si el usuario pide abrir un ticket o no puedes resolver, usa crear_ticket. "
        "Cuando el usuario pida guardar una preferencia (producto favorito, gustos, etc.), usa guardar_preferencia con el user_id que te indiquen en el contexto. "
        "Si una consulta mezcla temas, invoca los especialistas que correspondan. "
        "Responde en español de forma clara y útil."
    )
    return create_agent(
        model=settings.model_name,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        store=store,
        context_schema=Context,
    )
