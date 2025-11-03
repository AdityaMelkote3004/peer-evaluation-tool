"""API v1 router - aggregates all v1 endpoints."""
from fastapi import APIRouter
from app.api.v1 import auth, users, projects, teams, forms, evaluations, reports

api_router = APIRouter(prefix="/v1")

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(teams.router)
api_router.include_router(forms.router)
api_router.include_router(evaluations.router)
api_router.include_router(reports.router)
