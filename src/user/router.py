from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from src.user.model import User
from src.user.schema import UserSchema, UserLogin
from src.utils.auth_utils import pwd_context
import uuid
from fastapi import status
from src.utils.auth_utils import verify_password, create_access_token, get_current_user
from fastapi.exceptions import HTTPException
from datetime import timedelta 
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends


ACCESS_TOKEN_EXPIRE_MINUTE = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTE"])

auth_router = APIRouter()

@auth_router.post("/register", status_code=200)
def register_farmer(farmer : UserSchema, db : Session = Depends(get_db)):
    hashed_password = pwd_context.hash(farmer.password)

    if farmer.role.value == "government" and farmer.gov_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide your government id"
        )

    new_farmer = User(
        user_id = str(uuid.uuid4()),
        role = farmer.role.value,
        name = farmer.name,
        email = farmer.email,
        hashed_password = hashed_password,
    )

    db.add(new_farmer)
    db.commit()    

    return {
        "farmer" : new_farmer.user_id,
        "status" : status.HTTP_201_CREATED,
        "message": "Farmer registered successfully"
    }


@auth_router.post("/login", status_code=200)
async def login(data: UserLogin, db:Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email, User.is_deleted == False).first()
    # if db_farmer and verify_password(data.password, db_farmer.hashed_password):


    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)

    access_token = create_access_token(
        data={"sub": str(user.user_id), "role" : user.role},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



@auth_router.get("/token-data", status_code=200)
async def get_token_data(current_user : dict = Depends(get_current_user)):
    return current_user