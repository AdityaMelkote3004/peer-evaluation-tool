"""Evaluation submission and retrieval routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from app.db import get_db
from app.core.supabase import supabase

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


# Pydantic models
class EvaluationScore(BaseModel):
    criterion_id: int
    score: int


class EvaluationSubmit(BaseModel):
    form_id: int
    evaluator_id: int
    evaluatee_id: int
    team_id: int
    total_score: int
    scores: List[EvaluationScore]
    comments: Optional[str] = None


class EvaluationUpdate(BaseModel):
    total_score: Optional[int] = None
    comments: Optional[str] = None
    scores: Optional[List[EvaluationScore]] = None


@router.get("/")
async def list_evaluations(
    form_id: Optional[int] = None,
    team_id: Optional[int] = None,
    evaluator_id: Optional[int] = None,
    evaluatee_id: Optional[int] = None
):
    """List evaluations with optional filters."""
    try:
        query = supabase.table("evaluations").select("*")
        
        # Apply filters if provided
        if form_id:
            query = query.eq("form_id", form_id)
        if team_id:
            query = query.eq("team_id", team_id)
        if evaluator_id:
            query = query.eq("evaluator_id", evaluator_id)
        if evaluatee_id:
            query = query.eq("evaluatee_id", evaluatee_id)
        
        result = query.order("submitted_at", desc=True).execute()
        
        # Enrich each evaluation with related data
        evaluations = result.data
        for evaluation in evaluations:
            # Get evaluator details
            evaluator = supabase.table("users").select("id, name, email").eq("id", evaluation["evaluator_id"]).execute()
            evaluation["evaluator"] = evaluator.data[0] if evaluator.data else None
            
            # Get evaluatee details
            evaluatee = supabase.table("users").select("id, name, email").eq("id", evaluation["evaluatee_id"]).execute()
            evaluation["evaluatee"] = evaluatee.data[0] if evaluatee.data else None
            
            # Get team details
            team = supabase.table("teams").select("id, name").eq("id", evaluation["team_id"]).execute()
            evaluation["team"] = team.data[0] if team.data else None
            
            # Get form details
            form = supabase.table("evaluation_forms").select("id, title").eq("id", evaluation["form_id"]).execute()
            evaluation["form"] = form.data[0] if form.data else None
            
            # Get scores with criteria details
            scores = supabase.table("evaluation_scores").select("*").eq("evaluation_id", evaluation["id"]).execute()
            
            if scores.data:
                for score in scores.data:
                    criterion = supabase.table("form_criteria").select("*").eq("id", score["criterion_id"]).execute()
                    score["criterion"] = criterion.data[0] if criterion.data else None
                
                evaluation["scores"] = scores.data
            else:
                evaluation["scores"] = []
        
        return {
            "evaluations": evaluations,
            "count": len(evaluations),
            "message": "Evaluations retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evaluations: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_evaluation(evaluation_data: EvaluationSubmit):
    """Submit a new peer evaluation."""
    try:
        # Validate form exists
        form = supabase.table("evaluation_forms").select("*").eq("id", evaluation_data.form_id).execute()
        
        if not form.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation form not found"
            )
        
        # Validate team exists
        team = supabase.table("teams").select("*").eq("id", evaluation_data.team_id).execute()
        
        if not team.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Validate evaluator exists and is a team member
        evaluator = supabase.table("users").select("id").eq("id", evaluation_data.evaluator_id).execute()
        
        if not evaluator.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluator not found"
            )
        
        evaluator_member = supabase.table("team_members").select("*").eq("team_id", evaluation_data.team_id).eq("user_id", evaluation_data.evaluator_id).execute()
        
        if not evaluator_member.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluator is not a member of this team"
            )
        
        # Validate evaluatee exists and is a team member
        evaluatee = supabase.table("users").select("id").eq("id", evaluation_data.evaluatee_id).execute()
        
        if not evaluatee.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluatee not found"
            )
        
        evaluatee_member = supabase.table("team_members").select("*").eq("team_id", evaluation_data.team_id).eq("user_id", evaluation_data.evaluatee_id).execute()
        
        if not evaluatee_member.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluatee is not a member of this team"
            )
        
        # Prevent self-evaluation
        if evaluation_data.evaluator_id == evaluation_data.evaluatee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot evaluate yourself"
            )
        
        # Check for duplicate evaluation
        existing = supabase.table("evaluations").select("*").eq("form_id", evaluation_data.form_id).eq("evaluator_id", evaluation_data.evaluator_id).eq("evaluatee_id", evaluation_data.evaluatee_id).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already evaluated this team member for this form"
            )
        
        # Validate all criteria belong to the form
        form_criteria = supabase.table("form_criteria").select("id").eq("form_id", evaluation_data.form_id).execute()
        valid_criterion_ids = [c["id"] for c in form_criteria.data] if form_criteria.data else []
        
        for score in evaluation_data.scores:
            if score.criterion_id not in valid_criterion_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Criterion {score.criterion_id} does not belong to this form"
                )
        
        # Create evaluation
        new_evaluation = {
            "form_id": evaluation_data.form_id,
            "evaluator_id": evaluation_data.evaluator_id,
            "evaluatee_id": evaluation_data.evaluatee_id,
            "team_id": evaluation_data.team_id,
            "total_score": evaluation_data.total_score,
            "comments": evaluation_data.comments
        }
        
        result = supabase.table("evaluations").insert(new_evaluation).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create evaluation"
            )
        
        created_evaluation = result.data[0]
        evaluation_id = created_evaluation["id"]
        
        # Create scores
        scores_data = []
        for score in evaluation_data.scores:
            score_entry = {
                "evaluation_id": evaluation_id,
                "criterion_id": score.criterion_id,
                "score": score.score
            }
            score_result = supabase.table("evaluation_scores").insert(score_entry).execute()
            if score_result.data:
                scores_data.append(score_result.data[0])
        
        created_evaluation["scores"] = scores_data
        
        return {
            "evaluation": created_evaluation,
            "message": "Evaluation submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit evaluation: {str(e)}"
        )


@router.get("/{evaluation_id}")
async def get_evaluation(evaluation_id: int):
    """Get detailed evaluation by ID."""
    try:
        # Get evaluation
        result = supabase.table("evaluations").select("*").eq("id", evaluation_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        evaluation = result.data[0]
        
        # Get evaluator details
        evaluator = supabase.table("users").select("id, name, email").eq("id", evaluation["evaluator_id"]).execute()
        evaluation["evaluator"] = evaluator.data[0] if evaluator.data else None
        
        # Get evaluatee details
        evaluatee = supabase.table("users").select("id, name, email").eq("id", evaluation["evaluatee_id"]).execute()
        evaluation["evaluatee"] = evaluatee.data[0] if evaluatee.data else None
        
        # Get team details
        team = supabase.table("teams").select("*").eq("id", evaluation["team_id"]).execute()
        evaluation["team"] = team.data[0] if team.data else None
        
        # Get form details with criteria
        form = supabase.table("evaluation_forms").select("*").eq("id", evaluation["form_id"]).execute()
        evaluation["form"] = form.data[0] if form.data else None
        
        # Get scores with criteria details
        scores = supabase.table("evaluation_scores").select("*").eq("evaluation_id", evaluation_id).execute()
        
        if scores.data:
            for score in scores.data:
                criterion = supabase.table("form_criteria").select("*").eq("id", score["criterion_id"]).execute()
                score["criterion"] = criterion.data[0] if criterion.data else None
            
            evaluation["scores"] = scores.data
        else:
            evaluation["scores"] = []
        
        return {
            "evaluation": evaluation,
            "message": "Evaluation retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evaluation: {str(e)}"
        )


@router.put("/{evaluation_id}")
async def update_evaluation(evaluation_id: int, evaluation_data: EvaluationUpdate):
    """Update an existing evaluation."""
    try:
        # Check if evaluation exists
        existing = supabase.table("evaluations").select("*").eq("id", evaluation_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Build update dict
        update_data = {}
        if evaluation_data.total_score is not None:
            update_data["total_score"] = evaluation_data.total_score
        if evaluation_data.comments is not None:
            update_data["comments"] = evaluation_data.comments
        
        # Update evaluation if there are changes
        if update_data:
            result = supabase.table("evaluations").update(update_data).eq("id", evaluation_id).execute()
            
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update evaluation"
                )
        
        # Update scores if provided
        if evaluation_data.scores is not None:
            # Delete existing scores
            supabase.table("evaluation_scores").delete().eq("evaluation_id", evaluation_id).execute()
            
            # Insert new scores
            for score in evaluation_data.scores:
                score_entry = {
                    "evaluation_id": evaluation_id,
                    "criterion_id": score.criterion_id,
                    "score": score.score
                }
                supabase.table("evaluation_scores").insert(score_entry).execute()
        
        # Get updated evaluation
        updated = supabase.table("evaluations").select("*").eq("id", evaluation_id).execute()
        evaluation = updated.data[0] if updated.data else {}
        
        # Get scores
        scores = supabase.table("evaluation_scores").select("*").eq("evaluation_id", evaluation_id).execute()
        evaluation["scores"] = scores.data if scores.data else []
        
        return {
            "evaluation": evaluation,
            "message": "Evaluation updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update evaluation: {str(e)}"
        )


@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: int):
    """Delete an evaluation."""
    try:
        # Check if evaluation exists
        existing = supabase.table("evaluations").select("*").eq("id", evaluation_id).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Delete evaluation (cascade will handle scores)
        result = supabase.table("evaluations").delete().eq("id", evaluation_id).execute()
        
        return {
            "message": f"Evaluation {evaluation_id} deleted successfully",
            "deleted_evaluation": existing.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete evaluation: {str(e)}"
        )
