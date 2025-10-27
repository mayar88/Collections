from fastapi import APIRouter, HTTPException
from app.models.instructor_model import Instructor
from app.database import instructors_collection

router = APIRouter(prefix="/instructors", tags=["Instructors"])


@router.post("/")
def create_instructor(instructor: Instructor):
    if instructors_collection.find_one({"id": instructor.id}):
        raise HTTPException(status_code=400, detail="Instructor with this ID already exists.")
    instructors_collection.insert_one(instructor.dict())
    return {"message": "Instructor created successfully!", "instructor": instructor}


@router.get("/")
def get_instructors():
    instructors = list(instructors_collection.find({}, {"_id": 0}))
    return instructors


@router.get("/{instructor_id}")
def get_instructor(instructor_id: int):
    instructor = instructors_collection.find_one({"id": instructor_id}, {"_id": 0})
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return instructor


@router.put("/{instructor_id}")
def update_instructor(instructor_id: int, instructor: Instructor):
    result = instructors_collection.update_one(
        {"id": instructor_id},
        {"$set": instructor.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return {"message": "Instructor updated successfully!"}


@router.delete("/{instructor_id}")
def delete_instructor(instructor_id: int):
    result = instructors_collection.delete_one({"id": instructor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Instructor not found")
    return {"message": "Instructor deleted successfully!"}
