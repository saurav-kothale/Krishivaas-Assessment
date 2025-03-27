from database import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from src.utils.base_model import BaseModel


class User(Base, BaseModel):
    __tablename__ = "User"
    user_id = Column(String, primary_key=True)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)