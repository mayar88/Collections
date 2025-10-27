from fastapi import APIRouter, HTTPException
from app.models.session_model import Session
from app.database import sessions_collection, users_collection, instructors_collection

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/")
def create_session(session: Session):
    if sessions_collection.find_one({"id": session.id}):
        raise HTTPException(status_code=400, detail="Session with this ID already exists.")

    # Validate user_id exists
    user = users_collection.find_one({"id": session.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {session.user_id} does not exist.")

    # Validate instructor_id exists
    instructor = instructors_collection.find_one({"id": session.instructor_id}, {"_id": 0})
    if not instructor:
        raise HTTPException(status_code=404, detail=f"Instructor ID {session.instructor_id} does not exist.")

    # Embed user and instructor info
    session_data = session.model_dump()
    session_data["user"] = user
    session_data["instructor"] = instructor

    sessions_collection.insert_one(session_data)
    return {"message": "Session created successfully!", "session": session_data}


@router.get("/")
def get_sessions():
    sessions = list(sessions_collection.find({}, {"_id": 0}))
    return sessions


@router.get("/{session_id}")
def get_session(session_id: int):
    session = sessions_collection.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}")
def update_session(session_id: int, session: Session):
    # Validate user_id exists
    user = users_collection.find_one({"id": session.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail=f"User ID {session.user_id} does not exist.")

    # Validate instructor_id exists
    instructor = instructors_collection.find_one({"id": session.instructor_id}, {"_id": 0})
    if not instructor:
        raise HTTPException(status_code=404, detail=f"Instructor ID {session.instructor_id} does not exist.")

    # Embed user and instructor info
    session_data = session.dict()
    session_data["user"] = user
    session_data["instructor"] = instructor

    result = sessions_collection.update_one(
        {"id": session_id},
        {"$set": session_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Session updated successfully!", "session": session_data}


@router.delete("/{session_id}")
def delete_session(session_id: int):
    result = sessions_collection.delete_one({"id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully!"}
