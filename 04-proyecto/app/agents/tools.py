"""
Tools for the supervisor: buscar_documentacion (RAG), crear_ticket (structured), TavilySearch,
guardar_preferencia (long-term store).
Tickets are appended to a global list for GET /tickets.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from langchain.tools import tool
from langchain_tavily import TavilySearch

from app.agents.rag import get_vector_store
from app.core import langchain as lc

# Namespace and key for profile in store (same as users endpoint)
_PROFILE_NS = "perfil"
_PROFILE_KEY = "profile"

# In-memory list of tickets created by the agent (for GET /tickets)
_tickets: list[dict[str, Any]] = []


def get_tickets_list() -> list[dict[str, Any]]:
    return _tickets.copy()


def _buscar_documentacion_impl(query: str) -> str:
    vs = get_vector_store()
    if vs is None:
        return "La base de documentación no está disponible. Contacta al administrador."
    docs = vs.similarity_search(query, k=3)
    if not docs:
        return "No se encontró información relevante en la documentación."
    resultados = []
    for doc in docs:
        fuente = doc.metadata.get("source", "N/A")
        resultados.append(f"[Fuente: {fuente}]\n{doc.page_content}")
    return "\n\n---\n\n".join(resultados)


# Tool instance for RAG - must be created when vector_store is ready (used by supervisor)
def make_buscar_documentacion_tool():
    @tool
    def buscar_documentacion(query: str) -> str:
        """Busca información en la documentación interna del producto (manuales, políticas, FAQs).
        Usa esta herramienta cuando el usuario pregunte sobre procedimientos, garantías, códigos de error o datos de la empresa."""
        return _buscar_documentacion_impl(query)

    return buscar_documentacion


# TavilySearch is a class - we instantiate it
def make_tavily_tool():
    return TavilySearch(max_results=3)


# crear_ticket: structured output (Pydantic-like) and append to list
@tool
def crear_ticket(titulo: str, descripcion: str, prioridad: str = "media") -> str:
    """Crea un ticket de soporte con título, descripción y prioridad (baja, media, alta).
    Usa esta herramienta cuando el usuario solicite abrir un ticket o cuando no puedas resolver su consulta."""
    ticket_id = str(uuid.uuid4())[:8]
    _tickets.append({
        "id": ticket_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad.lower(),
    })
    return f"Ticket creado: ID {ticket_id}. Título: {titulo}. Prioridad: {prioridad}."


def _get_store():
    """Store (PostgresStore o InMemoryStore) set at app startup."""
    return lc.store


@tool
def guardar_preferencia(user_id: str, clave: str, valor: str) -> str:
    """Guarda una preferencia o dato de perfil del usuario en su perfil persistente.
    Usa esta herramienta cuando el usuario pida guardar algo como preferencia (ej. producto favorito, preferencias).
    user_id: el ID del usuario actual (te lo indican en el contexto de la conversación).
    clave: nombre de la preferencia (ej. producto_favorito, preferencia_producto).
    valor: valor a guardar (ej. Vigil Pro, Nubis R7)."""
    store = _get_store()
    if store is None:
        return "No se puede guardar la preferencia: el almacenamiento no está disponible."
    namespace = (_PROFILE_NS, user_id)
    try:
        existing = store.get(namespace, _PROFILE_KEY)
    except Exception:
        existing = None
    current = {}
    if existing is not None:
        v = existing.value if hasattr(existing, "value") else existing
        if isinstance(v, dict):
            current = dict(v)
    preferencias = current.get("preferencias")
    if isinstance(preferencias, dict):
        preferencias = dict(preferencias)
    elif isinstance(preferencias, str):
        try:
            preferencias = json.loads(preferencias) if preferencias else {}
        except json.JSONDecodeError:
            preferencias = {}
    else:
        preferencias = {}
    preferencias[clave] = valor
    current["preferencias"] = preferencias
    store.put(namespace, _PROFILE_KEY, current)
    return f"Preferencia guardada: {clave} = {valor}."
