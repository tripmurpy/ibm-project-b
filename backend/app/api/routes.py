from fastapi import APIRouter, Depends

from app.api.schemas import ChatRequest, ChatResponse
from app.application.chat import ChatService

router = APIRouter(prefix="/v1", tags=["chat"])


def get_chat_service() -> ChatService:
    from app.main import chat_service
    return chat_service


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    result = await service.handle(
        request_id=str(payload.request_id),
        thread_id=str(payload.thread_id) if payload.thread_id else None,
        question=payload.question,
        reply_to=payload.reply_to,
    )
    return ChatResponse.from_domain(result)
