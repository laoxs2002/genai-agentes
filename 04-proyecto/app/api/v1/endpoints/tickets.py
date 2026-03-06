from fastapi import APIRouter

from app.agents.tools import get_tickets_list
from app.schemas.responses import TicketResponse

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
async def list_tickets():
    tickets = get_tickets_list()
    return [TicketResponse(**t) for t in tickets]
