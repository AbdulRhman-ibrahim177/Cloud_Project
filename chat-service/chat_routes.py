from fastapi import APIRouter
from schemas import ChatRequest, ChatResponse
from chat_logic import generate_response
from kafka_producer import produce_chat_message

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
def receive_message(payload: ChatRequest):
    # 1. Process chat
    reply = generate_response(payload.message)

    # 2. Produce Kafka event
    produce_chat_message({
        "user_id": payload.user_id,
        "message": payload.message,
        "response": reply
    })

    return ChatResponse(
        user_id=payload.user_id,
        message=payload.message,
        response=reply
    )