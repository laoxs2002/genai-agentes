from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    user_id: str | None = None


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Contenido del mensaje del usuario.")


class UserProfileUpdate(BaseModel):
    nombre: str | None = None
    producto: str | None = None
    preferencias: str | None = None
