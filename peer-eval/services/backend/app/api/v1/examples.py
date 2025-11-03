"""Example: How to use Supabase in your endpoints.

This file demonstrates how to interact with Supabase tables
from your FastAPI endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.core.supabase import supabase

router = APIRouter(prefix="/examples", tags=["examples"])


@router.get("/users")
async def get_all_users():
    """Example: Fetch all users from Supabase."""
    try:
        response = supabase.table("users").select("*").execute()
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: int):
    """Example: Fetch a specific user."""
    try:
        response = supabase.table("users").select("*").eq("id", user_id).single().execute()
        return {
            "success": True,
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")


@router.post("/users")
async def create_user(name: str, email: str):
    """Example: Create a new user."""
    try:
        response = supabase.table("users").insert({
            "name": name,
            "email": email
        }).execute()
        return {
            "success": True,
            "data": response.data,
            "message": "User created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}")
async def update_user(user_id: int, name: str = None, email: str = None):
    """Example: Update a user."""
    try:
        update_data = {}
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
            
        response = supabase.table("users").update(update_data).eq("id", user_id).execute()
        return {
            "success": True,
            "data": response.data,
            "message": "User updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Example: Delete a user."""
    try:
        response = supabase.table("users").delete().eq("id", user_id).execute()
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Advanced queries examples

@router.get("/projects/filter")
async def filter_projects(status: str = None, limit: int = 10):
    """Example: Filter projects with query parameters."""
    try:
        query = supabase.table("projects").select("*")
        
        if status:
            query = query.eq("status", status)
        
        response = query.limit(limit).execute()
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/with-members")
async def get_teams_with_members():
    """Example: Fetch teams with related members (JOIN)."""
    try:
        # Supabase supports foreign key joins
        response = supabase.table("teams").select("""
            *,
            members:team_members(
                user:users(id, name, email)
            )
        """).execute()
        
        return {
            "success": True,
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evaluations/aggregate")
async def get_evaluation_stats():
    """Example: Aggregate queries with Supabase."""
    try:
        # Count evaluations by status
        response = supabase.rpc("get_evaluation_stats").execute()
        # Note: You'd need to create a PostgreSQL function for complex aggregations
        
        return {
            "success": True,
            "data": response.data
        }
    except Exception as e:
        # Fallback: manual aggregation
        evaluations = supabase.table("evaluations").select("status").execute()
        stats = {}
        for eval in evaluations.data:
            status = eval.get("status", "unknown")
            stats[status] = stats.get(status, 0) + 1
        
        return {
            "success": True,
            "data": stats
        }


# To use this router, add to app/api/v1/__init__.py:
# from app.api.v1 import examples
# api_router.include_router(examples.router)
