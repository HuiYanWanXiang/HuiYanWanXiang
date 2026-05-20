from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    is_root = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    used_count = Column(Integer, default=0)
    free_quota = Column(Integer, default=3)

    created_at = Column(DateTime(timezone=True), server_default=func.now())