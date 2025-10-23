from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    message = Column(Text)
    response = Column(Text, default="")
    status = Column(String, default="Новый")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
