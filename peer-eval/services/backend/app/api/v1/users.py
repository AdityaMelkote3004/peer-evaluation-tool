"""User management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.db import get_db
from app.core.supabase import supabase

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic models for request/response
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: str = "student"  # default to student
    password: str = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str


@router.get("/")
async def list_users():
    """List all users using Supabase."""
    try:
        response = supabase.table("users").select("*").execute()
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user(user_id: int):
    """Get user by ID using Supabase."""
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return {
            "success": True,
            "data": response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict)
async def create_user(user: UserCreate):
    """Create a new user using Supabase."""
    try:
        # Check if email already exists
        existing = supabase.table("users").select("id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user data
        user_data = {
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        
        # Add password hash if provided (in production, hash this!)
        if user.password:
            user_data["password_hash"] = user.password  # TODO: Hash this with bcrypt
        
        # Insert into Supabase
        response = supabase.table("users").insert(user_data).execute()
        
        return {
            "success": True,
            "data": response.data[0] if response.data else None,
            "message": "User created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}")
async def update_user(user_id: int, name: str = None, email: str = None, role: str = None):
    """Update a user using Supabase."""
    try:
        update_data = {}
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
        if role:
            update_data["role"] = role
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("users").update(update_data).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return {
            "success": True,
            "data": response.data[0],
            "message": "User updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """Delete a user using Supabase."""
    try:
        response = supabase.table("users").delete().eq("id", user_id).execute()
        
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
