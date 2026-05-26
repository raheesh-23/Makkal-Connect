from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any
import asyncio

from app.core.database import get_db
from app.models.domain import Volunteer, Event, Task, Announcement, District
from app.schemas.domain import VolunteerCreate, VolunteerResponse
from app.services.membership_id import generate_membership_id
from app.services.qr_service import generate_qr_code_base64
from app.api.v1.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=VolunteerResponse)
async def register_volunteer(volunteer_in: VolunteerCreate, db: AsyncSession = Depends(get_db)):
    # Verify the district exists
    district_result = await db.execute(select(District).where(District.id == volunteer_in.district_id))
    district = district_result.scalar_one_or_none()
    if not district:
        raise HTTPException(status_code=400, detail="Invalid district ID. District does not exist.")

    # Simple logic to generate ID based on count
    result = await db.execute(select(Volunteer))
    count = len(result.scalars().all()) + 1
    
    member_id = generate_membership_id("TN", 2026, count)
    qr_code = generate_qr_code_base64(member_id)
    
    volunteer = Volunteer(
        **volunteer_in.model_dump(),
        membership_id=member_id,
        qr_code_url=qr_code
    )
    db.add(volunteer)
    await db.commit()
    await db.refresh(volunteer)
    return volunteer

@router.get("/", response_model=List[VolunteerResponse])
async def get_volunteers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Volunteer))
    return result.scalars().all()

@router.patch("/{id}/approve", response_model=VolunteerResponse)
async def approve_volunteer(id: str, db: AsyncSession = Depends(get_db)):
    import uuid
    result = await db.execute(select(Volunteer).where(Volunteer.id == uuid.UUID(id)))
    volunteer = result.scalar_one_or_none()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
        
    volunteer.is_approved = True
    await db.commit()
    await db.refresh(volunteer)
    return volunteer

@router.get("/stats")
async def get_volunteer_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Volunteer))
    volunteers = result.scalars().all()
    
    district_counts = {}
    for v in volunteers:
        district_counts[v.district_id] = district_counts.get(v.district_id, 0) + 1
        
    return {
        "total_volunteers": len(volunteers),
        "district_counts": district_counts
    }

from app.models.domain import VolunteerPost
from app.schemas.domain import VolunteerPostCreate, VolunteerPostResponse

@router.post("/posts", response_model=VolunteerPostResponse)
async def create_volunteer_post(post_in: VolunteerPostCreate, membership_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Volunteer).where(Volunteer.membership_id == membership_id))
    volunteer = result.scalar_one_or_none()
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
        
    post = VolunteerPost(**post_in.model_dump(), volunteer_id=volunteer.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

@router.get("/posts", response_model=List[VolunteerPostResponse])
async def get_volunteer_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerPost))
    return result.scalars().all()
