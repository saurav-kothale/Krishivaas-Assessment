from pydantic import BaseModel
from enum import Enum

class Role(Enum):
    FARMER = "farmer"
    GOVERMENT = "government"


class UserSchema(BaseModel):
    name: str
    role: Role
    email: str
    password: str
    gov_id: str | None = None



class UserLogin(BaseModel):
    email : str
    password : str

    


    