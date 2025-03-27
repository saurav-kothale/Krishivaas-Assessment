from pydantic import BaseModel, Field

class FarmSchema(BaseModel):
    latitude: float 
    longitude: float 
    city: str 
    state: str 
    