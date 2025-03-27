from database import Base
from src.utils.base_model import BaseModel
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship


class Farm(Base, BaseModel):
    __tablename__ = "farm"
    farm_id = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("Farmer.user_id"), nullable=False)


