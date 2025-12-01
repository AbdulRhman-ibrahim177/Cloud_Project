from sqlalchemy import Column, Integer, String, Text
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    message = Column(Text, nullable=False)
