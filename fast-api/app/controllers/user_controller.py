from app.models.user_model import User
from app.database import users_collection
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users",tags=["Users"])


@router.post("/")
def create_user(user: User):
    if users_collection.find_one({"id": user.id}):
        raise HTTPException(status_code=400, detail="User already exists")
    users_collection.insert_one(user.dict())
    return {"message": "User created successfully!", "user": user}

@router.get("/")
def get_users():
    return list(users_collection.find({}, {"_id": 0}))

@router.get("/{user_id}")
def get_user(user_id: int):
    user = users_collection.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
def update_user(user_id: int, user: User):
    result = users_collection.update_one({"id": user_id}, {"$set": user.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully!"}

@router.delete("/{user_id}")
def delete_user(user_id: int):
    result = users_collection.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully!"}