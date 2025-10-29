# fast-api/main.py
from fastapi import FastAPI,Depends
from app.controllers.user_controller import router as user_router
from app.controllers.instructor_controller import router as instructor_router
from app.controllers.session_controller import router as session_router
from app.controllers import auth_controller

app = FastAPI()

# Register routers
app.include_router(auth_controller.router)
app.include_router(user_router)
app.include_router(instructor_router)
app.include_router(session_router)

@app.get("/protected")
def protected_route(current_user=Depends(auth_controller.verify_token)):
    return {"message": f"Hello user {current_user}"}

