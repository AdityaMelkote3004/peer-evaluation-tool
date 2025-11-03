"""Form/rubric management routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from app.db import get_db
from app.core.supabase import supabase

router = APIRouter(prefix="/forms", tags=["forms"])


# Pydantic models
class FormCriterion(BaseModel):
    text: str
    max_points: int
    order_index: int


class FormCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    max_score: int = 100
    criteria: List[FormCriterion]


class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    max_score: Optional[int] = None


class CriterionUpdate(BaseModel):
    text: Optional[str] = None
    max_points: Optional[int] = None
    order_index: Optional[int] = None


@router.get("/")
async def list_forms(project_id: Optional[int] = None):
    """List all evaluation forms with optional project filter."""
    try:
        query = supabase.table("evaluation_forms").select("*")
        
        # Filter by project if provided
        if project_id:
            query = query.eq("project_id", project_id)
        
        result = query.order("created_at", desc=True).execute()
        
        # Get criteria for each form
        forms = result.data
        for form in forms:
            # Get project details
            project = supabase.table("projects").select("id, title").eq("id", form["project_id"]).execute()
            form["project"] = project.data[0] if project.data else None
            
            # Get criteria
            criteria = supabase.table("form_criteria").select("*").eq("form_id", form["id"]).order("order_index").execute()
            form["criteria"] = criteria.data if criteria.data else []
            form["criteria_count"] = len(criteria.data) if criteria.data else 0
        
        return {
            "forms": forms,
            "count": len(forms),
            "message": "Evaluation forms retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve forms: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_form(form_data: FormCreate):
    """Create a new evaluation form with criteria."""
    try:
        # Verify project exists
        project = supabase.table("projects").select("*").eq("id", form_data.project_id).execute()
        
        if not project.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Validate criteria
        if not form_data.criteria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form must have at least one criterion"
            )
        
        # Check that max_points sum up reasonably
        total_points = sum(c.max_points for c in form_data.criteria)
        if total_points != form_data.max_score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sum of criterion max_points ({total_points}) should equal form max_score ({form_data.max_score})"
            )
        
        # Create form
        new_form = {
            "project_id": form_data.project_id,
            "title": form_data.title,
            "description": form_data.description,
            "max_score": form_data.max_score
        }
        
        result = supabase.table("evaluation_forms").insert(new_form).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create form"
            )
        
        created_form = result.data[0]
        form_id = created_form["id"]
        
        # Create criteria
        criteria_data = []
        for criterion in form_data.criteria:
            criterion_entry = {
                "form_id": form_id,
                "text": criterion.text,
                "max_points": criterion.max_points,
                "order_index": criterion.order_index
            }
            criterion_result = supabase.table("form_criteria").insert(criterion_entry).execute()
            if criterion_result.data:
                criteria_data.append(criterion_result.data[0])
        
        created_form["criteria"] = criteria_data
        
        return {
            "form": created_form,
            "message": f"Evaluation form created successfully with {len(criteria_data)} criteria"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create form: {str(e)}"
        )


@router.get("/{form_id}")
async def get_form(form_id: int):
    """Get evaluation form with all criteria."""
    try:
        # Get form
        result = supabase.table("evaluation_forms").select("*").eq("id", form_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation form not found"
            )
        
        form = result.data[0]
        
        # Get project details
        project = supabase.table("projects").select("*").eq("id", form["project_id"]).execute()
        form["project"] = project.data[0] if project.data else None
        
        # Get criteria
        criteria = supabase.table("form_criteria").select("*").eq("form_id", form_id).order("order_index").execute()
        form["criteria"] = criteria.data if criteria.data else []
        
        # Get usage statistics
        evaluations = supabase.table("evaluations").select("id").eq("form_id", form_id).execute()
        form["usage_count"] = len(evaluations.data) if evaluations.data else 0
        
        return {
            "form": form,
            "message": "Evaluation form retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve form: {str(e)}"
        )


@router.put("/{form_id}")
async def update_form(form_id: int, form_data: FormUpdate):
    """Update evaluation form details (not criteria)."""
    try:
        # Check if form exists
        existing = supabase.table("evaluation_forms").select("*").eq("id", form_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation form not found"
            )
        
        # Build update dict
        update_data = {}
        if form_data.title is not None:
            update_data["title"] = form_data.title
        if form_data.description is not None:
            update_data["description"] = form_data.description
        if form_data.max_score is not None:
            update_data["max_score"] = form_data.max_score
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Update form
        result = supabase.table("evaluation_forms").update(update_data).eq("id", form_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update form"
            )
        
        # Get updated form with criteria
        updated_form = result.data[0]
        criteria = supabase.table("form_criteria").select("*").eq("form_id", form_id).order("order_index").execute()
        updated_form["criteria"] = criteria.data if criteria.data else []
        
        return {
            "form": updated_form,
            "message": "Evaluation form updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update form: {str(e)}"
        )


@router.delete("/{form_id}")
async def delete_form(form_id: int):
    """Delete an evaluation form and all its criteria."""
    try:
        # Check if form exists
        existing = supabase.table("evaluation_forms").select("*").eq("id", form_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation form not found"
            )
        
        # Check if form is being used in evaluations
        evaluations = supabase.table("evaluations").select("id").eq("form_id", form_id).execute()
        
        if evaluations.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete form. It is being used in {len(evaluations.data)} evaluation(s)"
            )
        
        # Delete form (cascade will handle criteria)
        result = supabase.table("evaluation_forms").delete().eq("id", form_id).execute()
        
        return {
            "message": f"Evaluation form {form_id} deleted successfully",
            "deleted_form": existing.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete form: {str(e)}"
        )


@router.post("/{form_id}/criteria", status_code=status.HTTP_201_CREATED)
async def add_criterion(form_id: int, criterion_data: FormCriterion):
    """Add a new criterion to an existing form."""
    try:
        # Verify form exists
        form = supabase.table("evaluation_forms").select("*").eq("id", form_id).execute()
        
        if not form.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation form not found"
            )
        
        # Create criterion
        new_criterion = {
            "form_id": form_id,
            "text": criterion_data.text,
            "max_points": criterion_data.max_points,
            "order_index": criterion_data.order_index
        }
        
        result = supabase.table("form_criteria").insert(new_criterion).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add criterion"
            )
        
        return {
            "criterion": result.data[0],
            "message": "Criterion added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add criterion: {str(e)}"
        )


@router.put("/{form_id}/criteria/{criterion_id}")
async def update_criterion(form_id: int, criterion_id: int, criterion_data: CriterionUpdate):
    """Update a specific criterion."""
    try:
        # Verify criterion exists and belongs to form
        existing = supabase.table("form_criteria").select("*").eq("id", criterion_id).eq("form_id", form_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Criterion not found or does not belong to this form"
            )
        
        # Build update dict
        update_data = {}
        if criterion_data.text is not None:
            update_data["text"] = criterion_data.text
        if criterion_data.max_points is not None:
            update_data["max_points"] = criterion_data.max_points
        if criterion_data.order_index is not None:
            update_data["order_index"] = criterion_data.order_index
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Update criterion
        result = supabase.table("form_criteria").update(update_data).eq("id", criterion_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update criterion"
            )
        
        return {
            "criterion": result.data[0],
            "message": "Criterion updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update criterion: {str(e)}"
        )


@router.delete("/{form_id}/criteria/{criterion_id}")
async def delete_criterion(form_id: int, criterion_id: int):
    """Delete a criterion from a form."""
    try:
        # Verify criterion exists and belongs to form
        existing = supabase.table("form_criteria").select("*").eq("id", criterion_id).eq("form_id", form_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Criterion not found or does not belong to this form"
            )
        
        # Check if criterion is being used in evaluation scores
        scores = supabase.table("evaluation_scores").select("id").eq("criterion_id", criterion_id).execute()
        
        if scores.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete criterion. It is being used in {len(scores.data)} evaluation score(s)"
            )
        
        # Delete criterion
        result = supabase.table("form_criteria").delete().eq("id", criterion_id).execute()
        
        return {
            "message": f"Criterion {criterion_id} deleted successfully",
            "deleted_criterion": existing.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete criterion: {str(e)}"
        )
