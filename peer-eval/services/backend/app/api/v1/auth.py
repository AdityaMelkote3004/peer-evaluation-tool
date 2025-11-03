"""Authentication routes - login, register, etc."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.db import get_db
from app.core.supabase import supabase

router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "student"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    message: str


class LoginResponse(BaseModel):
    user: dict
    message: str
    # TODO: Add access_token field when JWT is implemented
    # access_token: str
    # token_type: str = "bearer"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user."""
    try:
        # Check if user already exists
        existing = supabase.table("users").select("*").eq("email", user_data.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user in database
        # TODO: Hash the password with bcrypt before storing
        new_user = {
            "email": user_data.email,
            "password_hash": user_data.password,  # TODO: Hash this!
            "name": user_data.name,
            "role": user_data.role
        }
        
        result = supabase.table("users").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        created_user = result.data[0]
        return {
            "id": created_user["id"],
            "email": created_user["email"],
            "name": created_user["name"],
            "role": created_user["role"],
            "message": "User registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    """Login user and return user data."""
    try:
        # Find user by email
        result = supabase.table("users").select("*").eq("email", credentials.email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = result.data[0]
        
        # Verify password
        # TODO: Use bcrypt to verify hashed password
        # For now, comparing plain text (INSECURE - fix this!)
        if user.get("password_hash") != credentials.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # TODO: Generate JWT token here
        # from datetime import datetime, timedelta
        # import jwt
        # token_data = {"sub": user["email"], "exp": datetime.utcnow() + timedelta(hours=24)}
        # access_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        
        return {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            },
            "message": "Login successful"
            # "access_token": access_token,
            # "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """Logout user."""
    # For stateless JWT authentication, logout is handled client-side
    # by deleting the token. Server doesn't need to do anything.
    # If you want to implement token blacklisting, add that logic here.
    
    # TODO: Implement token blacklisting if needed
    # - Store revoked tokens in Redis or database
    # - Check token against blacklist on each request
    
    return {
        "message": "Logout successful. Please delete your token on the client side.",
        "instructions": "Clear the authentication token from your application storage"
    }


@router.get("/me")
async def get_current_user(user_id: int):
    """Get current authenticated user by ID."""
    # TODO: Replace user_id parameter with JWT token verification
    # This should extract user_id from the JWT token, not accept it as a parameter
    # Example:
    # def get_current_user(token: str = Depends(oauth2_scheme)):
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    #     user_id = payload.get("sub")
    
    try:
        result = supabase.table("users").select("id, email, name, role, created_at").eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = result.data[0]
        return {
            "user": user,
            "message": "User retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )
