from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from src.utils.base_model import BaseModel


class Crop(Base, BaseModel):
    __tablename__ = 'crops'

    id = Column(String, primary_key=True)
    farm_id = Column(String, ForeignKey('farm.farm_id'), nullable=False)
    crop_type = Column(String, nullable=False)
    health_status = Column(String, nullable=False, default="pending")
    document_url = Column(String, nullable=True)


