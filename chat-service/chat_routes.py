from fastapi import APIRouter
from schemas import ChatRequest, ChatResponse
from chat_logic import generate_response
from kafka_producer import produce_chat_message

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
def receive_message(payload: ChatRequest):
    reply = generate_response(payload.message)

    # Send message to Kafka
    produce_chat_message(payload.user_id, payload.message)

    return ChatResponse(
        user_id=payload.user_id,
        message=payload.message,
        response=reply
    )