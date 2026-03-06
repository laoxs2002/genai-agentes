import uuid
from fastapi import APIRouter, Request, HTTPException, Body

from app.schemas.requests import ConversationCreate, MessageCreate
from app.schemas.responses import ConversationResponse, MessageResponse
from app.services.chat import invoke_supervisor

router = APIRouter(prefix="/conversations", tags=["conversations"])

# In-memory list of conversations: id -> { id, user_id }
_conversations: dict[str, dict] = {}


@router.post("", response_model=ConversationResponse)
async def create_conversation(body: ConversationCreate | None = Body(None)):
    conv_id = str(uuid.uuid4())
    user_id = body.user_id if body and body.user_id else None
    _conversations[conv_id] = {"id": conv_id, "user_id": user_id}
    return ConversationResponse(id=conv_id, user_id=_conversations[conv_id]["user_id"])


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(user_id: str | None = None):
    if user_id is None:
        return [ConversationResponse(id=c["id"], user_id=c["user_id"]) for c in _conversations.values()]
    return [
        ConversationResponse(id=c["id"], user_id=c["user_id"])
        for c in _conversations.values()
        if c.get("user_id") == user_id
    ]


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def post_message(conversation_id: str, body: MessageCreate, request: Request):
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv = _conversations[conversation_id]
    # user_id se obtiene siempre de la conversación (asociada al crearla)
    user_id = conv.get("user_id")
    result = invoke_supervisor(
        request=request,
        conversation_id=conversation_id,
        content=body.content,
        user_id=user_id,
    )
    return MessageResponse(
        role="assistant",
        content=result["content"],
        ticket_created=result.get("ticket_created"),
    )
