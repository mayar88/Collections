# fast-api/main.py
from fastapi import FastAPI

from app.controllers.user_controller import router as user_router
from app.controllers.instructor_controller import router as instructor_router
from app.controllers.session_controller import router as session_router

app = FastAPI()

# Register routers
app.include_router(user_router)
app.include_router(instructor_router)
app.include_router(session_router)

