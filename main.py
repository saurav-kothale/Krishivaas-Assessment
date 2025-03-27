from fastapi import FastAPI
import uvicorn
from src.user.router import auth_router
from src.farm.router import farm_router
from src.crop.router import crop_router

app = FastAPI()

app.include_router(auth_router,tags=["authentication"])
app.include_router(farm_router, tags=["Farm"])
app.include_router(crop_router, tags=["Crop"])


@app.get("/")
def get_function():
    return{
        "message" : "server is running perfectly"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)