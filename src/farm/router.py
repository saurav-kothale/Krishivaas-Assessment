from src.farm.model import Farm
from src.farm.schema import FarmSchema
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends
from database import get_db  
from src.utils.auth_utils import get_current_user
import uuid
from fastapi.exceptions import HTTPException


farm_router = APIRouter()


@farm_router.post('/farm', status_code=status.HTTP_201_CREATED)
def create_farm(schema: FarmSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "farmer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not elegeble to create a farm"
        )

    new_farm = Farm(
        farm_id=str(uuid.uuid4()),  # Generate a unique ID for the farm
        latitude=schema.latitude,
        longitude=schema.longitude,
        city=schema.city,
        state=schema.state,
        user_id=current_user.get("user_id")
    )
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    return {
        "farm": new_farm,
        "message": "Farm created successfully", 
        "status" : status.HTTP_200_OK
    }


@farm_router.get('/farms', status_code=status.HTTP_200_OK)
def get_all_farms(db: Session = Depends(get_db)):
    farms = db.query(Farm).filter(Farm.is_deleted == False).all()

    if not farms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="farm not found"
        )

    return {
        "farm" : farms,
        "message" : "farms Fetched Successfully",
        "status" : status.HTTP_200_OK
    }

# Get a single farm by ID
@farm_router.get('/farm/{farm_id}', status_code=status.HTTP_200_OK)
def get_farm_by_id(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.farm_id == farm_id, Farm.is_deleted == False).first()

    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    
    return {
        "farm": farm,
        "message" : "farm Fetched Successfully",
        "status" : status.HTTP_200_OK
    }

# Update a farm
@farm_router.put('/farm/{farm_id}', status_code=status.HTTP_200_OK)
def update_farm(farm_id: str, schema: FarmSchema, db: Session = Depends(get_db), current_user : str = Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.farm_id == farm_id, Farm.is_deleted == False).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    
    farm.latitude = schema.latitude
    farm.longitude = schema.longitude
    farm.city = schema.city
    farm.state = schema.state
    farm.farmer_id = current_user 

    db.commit()
    db.refresh(farm)

    return {
        "farm": farm, 
        "message": "Farm updated successfully", 
        "status" : status.HTTP_200_OK
    }

# Delete a farm
@farm_router.delete('/farm/{farm_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: str, db: Session = Depends(get_db)):

    farm = db.query(Farm).filter(Farm.farm_id == farm_id, Farm.is_deleted == False).first()

    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    
    farm.is_deleted = True  
    db.commit()

    return {
        "farm" : farm_id,
        "message": "Farm marked as deleted successfully",
        "status" : status.HTTP_200_OK
    }
    