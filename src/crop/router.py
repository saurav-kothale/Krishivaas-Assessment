from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, status
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from uuid import uuid4
from fastapi import BackgroundTasks
import os
from sqlalchemy.orm import Session
from database import get_db
from src.utils.auth_utils import get_current_user
from src.user.model import User
from src.crop.model import Crop
from src.farm.model import Farm
from src.crop.schema import CropSchema, GovSchema

AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

crop_router = APIRouter()

s3_client = boto3.client(
    's3',
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY

)
BUCKET_NAME = "krushitech"

def upload_to_s3(file_content, unique_filename, content_type):
    try:
        # Upload file to S3
        s3_client.put_object(
            Bucket = BUCKET_NAME,
            Key = unique_filename,
            Body = file_content,
            ContentType = content_type
        )
    except (NoCredentialsError, PartialCredentialsError):

        print("AWS credentials not configured properly")
    except Exception as e:

        print(f"An error occurred during S3 upload: {str(e)}")



@crop_router.post("/upload_media", status_code=200)
async def upload_media(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:

        allowed_types = ["image/", "audio/", "video/"]
        if not any(file.content_type.startswith(t) for t in allowed_types):
            raise HTTPException(status_code=400, detail="Unsupported file type")


        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"

        file_content = await file.read()

        background_tasks.add_task(upload_to_s3, file_content, unique_filename, file.content_type)

        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"

        return {"file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


    

@crop_router.post("/farmer", status_code=201)
async def upload_crop_media(
    crop_schema: CropSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "farmer":
        raise HTTPException(status_code=404, detail="You do not have permission to create crop media")

 
    farm = db.query(Farm).filter(Farm.farm_id == crop_schema.farm_id, Farm.user_id == current_user["user_id"]).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or access denied")


    new_crop = Crop(
        id=str(uuid4()),
        farm_id= crop_schema.farm_id,
        crop_type=crop_schema.crop_type.value,
        document_url=crop_schema.document_url,
        user_id = current_user.get("user_id")
    )

    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)

    return {
        "crop": new_crop,
        "status" : status.HTTP_201_CREATED,
        "message": "Crop media uploaded successfully"
    }

@crop_router.get("/farmer")
def get_crop(db : Session = Depends(get_db), current_user : dict = Depends(get_current_user)):

    user_id = current_user.get("user_id")

    crops = db.query(Crop).filter(Crop.user_id == user_id, Crop.is_deleted == False).all()
    
    if not crops:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail= "No crop found"
        )
    
    crop_dict = [{
                    "id": crop.id, 
                    "farm_id": crop.farm_id, 
                    "crop_type": crop.crop_type, 
                    "health_status": crop.health_status
                    
                } for crop in crops]
    
    return {
        "crop" : crop_dict,
        "status" : status.HTTP_200_OK,
        "message" : "Record Fetched Successfully"        
    }  

@crop_router.put("/farmer/{crop_id}", status_code=200)
def update_farmer_crop(
    crop_id: str,
    crop_schema: CropSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "farmer":
        raise HTTPException(status_code=403, detail="Access denied")

    crop = db.query(Crop).filter(Crop.id == crop_id, Crop.user_id == current_user["user_id"], Crop.is_deleted == False).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found or access denied")

    crop.crop_type = crop_schema.crop_type.value
    crop.document_url = crop_schema.document_url
    db.commit()
    db.refresh(crop)

    return {
        "crop": crop,
        "status": status.HTTP_200_OK,
        "message": "Crop updated successfully",
    }

@crop_router.delete("/farmer/{crop_id}", status_code=200)
def delete_farmer_crop(
    crop_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "farmer":
        raise HTTPException(status_code=403, detail="Access denied")

    crop = db.query(Crop).filter(Crop.id == crop_id, Crop.user_id == current_user["user_id"], Crop.is_deleted == False).first()
    
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found or access denied")

    crop.is_deleted = True
    db.commit()

    return {
        "status": status.HTTP_200_OK,
        "message": "Crop deleted successfully",
    }


@crop_router.get("/gov/crop", status_code=200)
def get_crop_status(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:

        if current_user.get("role") == "goverment":

            pending_crops = db.query(Crop).filter(Crop.is_delete == False).all()
            return {
                "pending_crops": [{
                    "id": crop.id, 
                    "farm_id": crop.farm_id, 
                    "crop_type": crop.crop_type, 
                    "health_status": crop.health_status
                    
                } for crop in pending_crops]
            }
        
        else:
            raise HTTPException(status_code=403, detail="Access forbidden: User is not authorized to view this resource")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@crop_router.put("/gov/update/{crop_id}", status_code=200)
def update_crop_health_status(
    crop_id: str,
    schema: GovSchema,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
  
    if current_user["role"] != "government":

        raise HTTPException(status_code=403, detail="Access denied")

    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    crop.health_status = schema.health_status.value
    db.commit()
    db.refresh(crop)

    return {
        "crop": crop,
        "status" : status.HTTP_202_ACCEPTED,
        "message": "Crop health status updated successfully",
        
    }


@crop_router.get("/gov/pending_health_status", status_code=200)
def get_pending_health_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    if current_user["role"] != "government":
        raise HTTPException(status_code=403, detail="Access denied")

    pending_crops = db.query(Crop).filter(Crop.health_status == "pending", Crop.is_deleted == False).all()

    return {"pending_crops": [crop.to_dict() for crop in pending_crops]}


@crop_router.get("gov/get_crop/{city}/{state}", status_code=200)
def get_crop_by_location(
    city: str,
    state: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "government":
        raise HTTPException(status_code=403, detail="Access denied")

    pending_crops = db.query(Crop).join(Farm).filter(
        Crop.health_status == "pending",
        Crop.is_deleted == False,
        Farm.city == city,
        Farm.state == state
    ).all()

    if not pending_crops:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No pending crops found for the specified location"
        )

    return {
        "pending_crops": [crop.to_dict() for crop in pending_crops],
        "status": status.HTTP_200_OK,
        "message": "Pending crops fetched successfully"
    }

    
