from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.database import get_db
from app.models.domain import Volunteer, Complaint, CharityCampaign, WorkStatus, VolunteerPost

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    volunteers = await db.scalar(select(func.count()).select_from(Volunteer))
    complaints_pending = await db.scalar(
        select(func.count()).select_from(Complaint).where(Complaint.status == WorkStatus.pending)
    )
    campaigns_active = await db.scalar(select(func.count()).select_from(CharityCampaign))
    
    return {
        "total_volunteers": volunteers or 0,
        "pending_complaints": complaints_pending or 0,
        "active_campaigns": campaigns_active or 0
    }

@router.get("/activity")
async def get_dashboard_activity(db: AsyncSession = Depends(get_db)):
    # Fetch recent complaints
    complaints = await db.execute(select(Complaint).order_by(desc(Complaint.created_at)).limit(5))
    complaints = complaints.scalars().all()
    
    # Fetch recent volunteer posts
    posts = await db.execute(select(VolunteerPost).order_by(desc(VolunteerPost.created_at)).limit(5))
    posts = posts.scalars().all()
    
    activities = []
    for c in complaints:
        activities.append({
            "type": "complaint",
            "title": f"New Issue Reported: {c.category}",
            "description": c.description,
            "created_at": c.created_at,
            "status": c.status.value if c.status else "Pending"
        })
        
    for p in posts:
        activities.append({
            "type": "volunteer_post",
            "title": f"Volunteer Work Update",
            "description": p.description,
            "created_at": p.created_at,
            "status": "Verified"
        })
        
    # Sort combined activities by created_at descending
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    return activities[:10]
