from fastapi import FastAPI
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
instructors_collection = db["instructors"]
sessions_collection = db["sessions"]


@app.get("/")
def root():
    return {"message": "MongoDB connected and collections ready!"}

#Define a User model for request validation
class User(BaseModel):
    id: int
    username: str
    level: str

#Define a Instructor model for request validation
class Instructor(BaseModel):
    id: int
    name: str
    role: Optional[str] = None          # present if human
    model_version: Optional[str] = None # present if AI model
    expertise: str

#Session
class Session(BaseModel):
    id: int
    topic: str
    date: str
    instructor_id: int
    user_id: int


#create user
@app.post("/users")
def create_user(user: User):
    # Check if user with same id already exists
    if users_collection.find_one({"id": user.id}):
        return {"error": "User with this ID already exists."}

    # Insert user
    users_collection.insert_one(user.dict())
    return {"message": "User created successfully!", "user": user}

@app.get("/users")
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))  # exclude MongoDB _id field
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = users_collection.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return {"error": "User not found"}
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    result = users_collection.update_one(
        {"id": user_id},
        {"$set": user.dict()}
    )
    if result.matched_count == 0:
        return {"error": "User not found"}
    return {"message": "User updated successfully!"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    result = users_collection.delete_one({"id": user_id})
    if result.deleted_count == 0:
        return {"error": "User not found"}
    return {"message": "User deleted successfully!"}


@app.post("/instructors")
def create_instructor(instructor: Instructor):
    if instructors_collection.find_one({"id": instructor.id}):
        return {"error": "Instructor with this ID already exists."}

    instructors_collection.insert_one(instructor.dict())
    return {"message": "Instructor created successfully!", "instructor": instructor}

@app.get("/instructors")
def get_instructors():
    instructors = list(instructors_collection.find({}, {"_id": 0}))
    return instructors

@app.get("/instructors/{instructor_id}")
def get_instructor(instructor_id: int):
    instructor = instructors_collection.find_one({"id": instructor_id}, {"_id": 0})  # exclude _id
    if not instructor:
        return {"error": "Instructor not found"}
    return instructor


@app.put("/instructors/{instructor_id}")
def update_instructor(instructor_id: int, instructor: Instructor):
    # Update the instructor document
    result = instructors_collection.update_one(
        {"id": instructor_id},  # find by id
        {"$set": instructor.dict()}  # set new values
    )

    if result.matched_count == 0:
        return {"error": "Instructor not found"}

    return {"message": "Instructor updated successfully!"}


@app.delete("/instructors/{instructor_id}")
def delete_instructor(instructor_id: int):
    result = instructors_collection.delete_one({"id": instructor_id})

    if result.deleted_count == 0:
        return {"error": "Instructor not found"}

    return {"message": "Instructor deleted successfully!"}


@app.post("/sessions")
def create_session(session: Session):
    # Check session ID
    if sessions_collection.find_one({"id": session.id}):
        return {"error": "Session with this ID already exists."}

    # Validate user_id exists
    user = users_collection.find_one({"id": session.user_id}, {"_id": 0})
    if not user:
        return {"error": f"User ID {session.user_id} does not exist."}

    # Validate instructor_id exists
    instructor = instructors_collection.find_one({"id": session.instructor_id}, {"_id": 0})
    if not instructor:
        return {"error": f"Instructor ID {session.instructor_id} does not exist."}

    # Embed user and instructor info
    session_data = session.model_dump()
    session_data["user"] = user
    session_data["instructor"] = instructor

    sessions_collection.insert_one(session_data)
    return {"message": "Session created successfully!", "session": session_data}

@app.get("/sessions")
def get_sessions():
    sessions = list(sessions_collection.find({}, {"_id": 0}))  # exclude MongoDB _id
    return sessions

@app.get("/sessions/{session_id}")
def get_session(session_id: int):
    session = sessions_collection.find_one({"id": session_id}, {"_id": 0})
    if not session:
        return {"error": "Session not found"}
    return session

@app.put("/sessions/{session_id}")
def update_session(session_id: int, session: Session):
    # Validate user_id exists
    user = users_collection.find_one({"id": session.user_id}, {"_id": 0})
    if not user:
        return {"error": f"User ID {session.user_id} does not exist."}

    # Validate instructor_id exists
    instructor = instructors_collection.find_one({"id": session.instructor_id}, {"_id": 0})
    if not instructor:
        return {"error": f"Instructor ID {session.instructor_id} does not exist."}

    # Embed user and instructor info
    session_data = session.dict()
    session_data["user"] = user
    session_data["instructor"] = instructor

    # Update the session
    result = sessions_collection.update_one(
        {"id": session_id},
        {"$set": session_data}
    )

    if result.matched_count == 0:
        return {"error": "Session not found"}

    return {"message": "Session updated successfully!", "session": session_data}

@app.delete("/sessions/{session_id}")
def delete_session(session_id: int):
    result = sessions_collection.delete_one({"id": session_id})
    if result.deleted_count == 0:
        return {"error": "Session not found"}
    return {"message": "Session deleted successfully!"}
