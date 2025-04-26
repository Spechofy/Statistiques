from fastapi import FastAPI, HTTPException
from .schemas import CompatibilityRequest, CompatibilityResponse
from .crud import CRUD
from .database import db

app = FastAPI()

@app.on_event("shutdown")
def shutdown_event():
    db.close()

@app.get("/users/{user_id}/compatibility/top")
async def get_top_compatible_users(user_id: str, limit: int = 5):
    try:
        return CRUD.get_top_compatible_users(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/compatibility/", response_model=CompatibilityResponse)
async def calculate_compatibility(pair: CompatibilityRequest):
    try:
        result = CRUD.get_user_compatibility(pair.user1_id, pair.user2_id)
        if not result:
            raise HTTPException(status_code=404, detail="Users not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))