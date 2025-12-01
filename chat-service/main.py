from fastapi import FastAPI
from chat_routes import router as chat_router
from kafka_consumer import start_consumer_in_thread

app = FastAPI(title="Chat Service")

# Include routes
app.include_router(chat_router, prefix="/api/chat")

# Start Kafka Consumer in background thread when app starts
@app.on_event("startup")
def startup_event():
    start_consumer_in_thread()

@app.get("/")
def health():
    return {"status": "chat service running"}