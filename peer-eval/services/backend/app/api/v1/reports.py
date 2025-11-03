"""Reports and analytics routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.core.supabase import supabase
from collections import defaultdict

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/project/{project_id}")
async def get_project_report(project_id: int):
    """Get comprehensive evaluation report for a project."""
    try:
        # Verify project exists
        project = supabase.table("projects").select("*").eq("id", project_id).execute()
        
        if not project.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project_info = project.data[0]
        
        # Get all teams in the project
        teams = supabase.table("teams").select("*").eq("project_id", project_id).execute()
        
        report = {
            "project": project_info,
            "teams": [],
            "overall_statistics": {
                "total_teams": len(teams.data) if teams.data else 0,
                "total_evaluations": 0,
                "average_score": 0,
                "participation_rate": 0
            }
        }
        
        if not teams.data:
            return {
                "report": report,
                "message": "No teams found in this project"
            }
        
        total_evaluations = 0
        all_scores = []
        
        # Process each team
        for team in teams.data:
            team_report = await _get_team_data(team["id"])
            report["teams"].append(team_report)
            total_evaluations += team_report["statistics"]["total_evaluations"]
            all_scores.extend(team_report["statistics"].get("all_scores", []))
        
        # Calculate overall statistics
        report["overall_statistics"]["total_evaluations"] = total_evaluations
        if all_scores:
            report["overall_statistics"]["average_score"] = round(sum(all_scores) / len(all_scores), 2)
        
        return {
            "report": report,
            "message": "Project report generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate project report: {str(e)}"
        )


@router.get("/team/{team_id}")
async def get_team_report(team_id: int):
    """Get detailed evaluation report for a specific team."""
    try:
        # Verify team exists
        team = supabase.table("teams").select("*").eq("id", team_id).execute()
        
        if not team.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        team_report = await _get_team_data(team_id)
        
        return {
            "report": team_report,
            "message": "Team report generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate team report: {str(e)}"
        )


@router.get("/user/{user_id}")
async def get_user_report(user_id: int):
    """Get evaluation report for a specific user across all their teams."""
    try:
        # Verify user exists
        user = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_info = user.data[0]
        
        # Get all teams the user is a member of
        memberships = supabase.table("team_members").select("team_id").eq("user_id", user_id).execute()
        
        if not memberships.data:
            return {
                "report": {
                    "user": user_info,
                    "teams": [],
                    "overall_statistics": {
                        "teams_count": 0,
                        "evaluations_received": 0,
                        "evaluations_given": 0,
                        "average_score_received": 0
                    }
                },
                "message": "User is not a member of any team"
            }
        
        team_ids = [m["team_id"] for m in memberships.data]
        
        # Get evaluations received by this user
        evaluations_received = supabase.table("evaluations").select("*").eq("evaluatee_id", user_id).execute()
        
        # Get evaluations given by this user
        evaluations_given = supabase.table("evaluations").select("*").eq("evaluator_id", user_id).execute()
        
        # Calculate statistics
        scores_received = [e["total_score"] for e in evaluations_received.data if e.get("total_score")]
        avg_score = round(sum(scores_received) / len(scores_received), 2) if scores_received else 0
        
        # Get team details
        teams_data = []
        for team_id in team_ids:
            team = supabase.table("teams").select("*").eq("id", team_id).execute()
            if team.data:
                team_info = team.data[0]
                # Get evaluations for this user in this team
                team_evals = [e for e in evaluations_received.data if e["team_id"] == team_id]
                team_scores = [e["total_score"] for e in team_evals if e.get("total_score")]
                
                teams_data.append({
                    "team": team_info,
                    "evaluations_count": len(team_evals),
                    "average_score": round(sum(team_scores) / len(team_scores), 2) if team_scores else 0
                })
        
        report = {
            "user": {
                "id": user_info["id"],
                "name": user_info["name"],
                "email": user_info["email"],
                "role": user_info["role"]
            },
            "teams": teams_data,
            "overall_statistics": {
                "teams_count": len(team_ids),
                "evaluations_received": len(evaluations_received.data),
                "evaluations_given": len(evaluations_given.data),
                "average_score_received": avg_score
            },
            "detailed_evaluations": evaluations_received.data
        }
        
        return {
            "report": report,
            "message": "User report generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate user report: {str(e)}"
        )


@router.get("/evaluation-form/{form_id}")
async def get_form_report(form_id: int):
    """Get statistical report for a specific evaluation form."""
    try:
        # Get form details
        form = supabase.table("evaluation_forms").select("*").eq("id", form_id).execute()
        
        if not form.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation form not found"
            )
        
        form_info = form.data[0]
        
        # Get all criteria for this form
        criteria = supabase.table("form_criteria").select("*").eq("form_id", form_id).order("order_index").execute()
        
        # Get all evaluations using this form
        evaluations = supabase.table("evaluations").select("*").eq("form_id", form_id).execute()
        
        # Get all scores for this form
        if evaluations.data:
            evaluation_ids = [e["id"] for e in evaluations.data]
            all_scores = supabase.table("evaluation_scores").select("*").in_("evaluation_id", evaluation_ids).execute()
            
            # Aggregate scores by criterion
            criterion_stats = defaultdict(list)
            for score in all_scores.data:
                criterion_stats[score["criterion_id"]].append(score["score"])
            
            # Build criteria statistics
            criteria_analysis = []
            for criterion in criteria.data:
                scores = criterion_stats.get(criterion["id"], [])
                criteria_analysis.append({
                    "criterion": criterion,
                    "statistics": {
                        "total_responses": len(scores),
                        "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
                        "max_score": max(scores) if scores else 0,
                        "min_score": min(scores) if scores else 0
                    }
                })
        else:
            criteria_analysis = [{"criterion": c, "statistics": {"total_responses": 0, "average_score": 0}} for c in criteria.data]
        
        report = {
            "form": form_info,
            "criteria_analysis": criteria_analysis,
            "overall_statistics": {
                "total_evaluations": len(evaluations.data),
                "completion_rate": "N/A"  # Would need to know expected evaluations
            }
        }
        
        return {
            "report": report,
            "message": "Evaluation form report generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate form report: {str(e)}"
        )


# Helper function to get team data
async def _get_team_data(team_id: int) -> dict:
    """Helper function to get comprehensive team data."""
    team = supabase.table("teams").select("*").eq("id", team_id).execute()
    team_info = team.data[0] if team.data else {}
    
    # Get team members
    members = supabase.table("team_members").select("*").eq("team_id", team_id).execute()
    
    team_members = []
    if members.data:
        for member in members.data:
            user = supabase.table("users").select("id, name, email").eq("id", member["user_id"]).execute()
            if user.data:
                team_members.append(user.data[0])
    
    # Get all evaluations for this team
    evaluations = supabase.table("evaluations").select("*").eq("team_id", team_id).execute()
    
    # Calculate member statistics
    member_stats = {}
    all_scores = []
    
    for member in team_members:
        member_evals = [e for e in evaluations.data if e["evaluatee_id"] == member["id"]]
        scores = [e["total_score"] for e in member_evals if e.get("total_score")]
        all_scores.extend(scores)
        
        member_stats[member["id"]] = {
            "member": member,
            "evaluations_received": len(member_evals),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "evaluations": member_evals
        }
    
    return {
        "team": team_info,
        "members": list(member_stats.values()),
        "statistics": {
            "total_members": len(team_members),
            "total_evaluations": len(evaluations.data),
            "average_score": round(sum(all_scores) / len(all_scores), 2) if all_scores else 0,
            "all_scores": all_scores
        }
    }
