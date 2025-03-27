from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class BaseModel:
    """A simple base model to add timestamps and soft delete."""
    
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
