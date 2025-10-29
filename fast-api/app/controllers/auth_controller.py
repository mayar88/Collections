# fastapi/controllers/auth_controller.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app.database import users_collection
from app.models.user_model import User
import os
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
from typing import Dict

# Load environment variables
load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "1"))

# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Create router
router = APIRouter(prefix="/auth", tags=["Auth"])


# --- Helper Functions ---

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    Truncates to 72 bytes BEFORE hashing to avoid passlib error.
    """
    if not password:
        raise ValueError("Password cannot be empty")

    # Truncate to 72 bytes (bcrypt limit)
    password_bytes = password.encode("utf-8")[:72]
    password_truncated = password_bytes.decode("utf-8", "ignore")

    return pwd_context.hash(password_truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    Truncates input to 72 bytes for consistency.
    """
    password_bytes = plain_password.encode("utf-8")[:72]
    plain_truncated = password_bytes.decode("utf-8", "ignore")
    return pwd_context.verify(plain_truncated, hashed_password)


def create_access_token(data: Dict[str, str]) -> str:
    """
    Create JWT access token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Verify JWT token and return user ID.
    Raises 401 if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        return user_id
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        ) from e


# --- Auth Endpoints ---

@router.post("/signup")
def signup(user: User):

    try:
        # Check if username already exists
        if users_collection.find_one({"username": user.username}):
            return {"success": False, "message": "Username already exists"}

        # Convert Pydantic model to dict and hash password
        user_dict = user.model_dump()
        user_dict["password"] = hash_password(user.password)

        # Insert into MongoDB
        result = users_collection.insert_one(user_dict)
        user_id = str(result.inserted_id)

        return {
            "success": True,
            "message": "User created successfully",
            "user_id": user_id
        }

    except PyMongoError as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    except ValueError as e:
        return {"success": False, "message": f"Validation error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}


@router.post("/login")
def login(username: str, password: str):
    """
    Authenticate user and return JWT token.
    """
    try:
        user = users_collection.find_one({"username": username})
        if not user or not verify_password(password, user["password"]):
            return {"success": False, "message": "Invalid username or password"}

        # Generate JWT token
        access_token = create_access_token({"sub": str(user["_id"])})

        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600
        }

    except PyMongoError as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}