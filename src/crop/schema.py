from pydantic import BaseModel
from enum import Enum


class CropType(Enum):
    CEREAL = "cereal"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    LEGUME = "legume"
    TUBER = "tuber"
    OILSEED = "oilseed"

class HealthStatus(Enum):
    PENDING = "pending"
    HEALTHY = "healthy"
    DISEASED = "diseased"
    INFESTED = "infested"
    HARVESTED = "harvested"
    WILTED = "wilted"
    DAMAGED = "damaged"

class CropSchema(BaseModel):
    farm_id : str
    crop_type : CropType
    document_url : str

class GovSchema(BaseModel):
    health_status : HealthStatus