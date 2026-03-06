from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    id: str
    user_id: str | None = None


class MessageResponse(BaseModel):
    role: str
    content: str
    ticket_created: bool | None = None


class UserProfile(BaseModel):
    user_id: str
    nombre: str | None = None
    producto: str | None = None
    preferencias: str | dict | None = None  # dict cuando las guarda el agente (clave -> valor)


class TicketResponse(BaseModel):
    id: str
    titulo: str
    descripcion: str
    prioridad: str


class IndexDocsResponse(BaseModel):
    status: str = "ok"
    chunks_indexed: int
