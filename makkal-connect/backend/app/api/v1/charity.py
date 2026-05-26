from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any

from app.core.database import get_db
from app.models.domain import CharityCampaign, WelfareRequest, BloodDonor
from app.schemas.domain import CharityCampaignResponse, CharityCampaignBase
from app.api.v1.auth import get_current_user
from app.services.notifications import send_sms

router = APIRouter()

@router.get("/campaigns", response_model=List[CharityCampaignResponse])
async def get_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CharityCampaign))
    return result.scalars().all()

@router.post("/campaigns", response_model=CharityCampaignResponse)
async def create_campaign(campaign_in: CharityCampaignBase, db: AsyncSession = Depends(get_db)):
    campaign = CharityCampaign(**campaign_in.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign

@router.get("/donors")
async def get_blood_donors(blood_group: str = None, district_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(BloodDonor)
    if blood_group:
        query = query.where(BloodDonor.blood_group == blood_group)
    if district_id:
        query = query.where(BloodDonor.district_id == district_id)
        
    result = await db.execute(query)
    donors = result.scalars().all()
    return [{"id": d.id, "name": d.name, "masked_name": f"{d.name[0]}***", "phone": d.phone, "blood_group": d.blood_group} for d in donors]

@router.post("/donors")
async def add_blood_donor(donor_in: dict, db: AsyncSession = Depends(get_db)):
    import uuid
    new_donor = BloodDonor(
        id=uuid.uuid4(),
        name=donor_in.get("name"),
        blood_group=donor_in.get("blood_group"),
        phone=donor_in.get("phone"),
        district_id=int(donor_in.get("district_id", 1)),
        is_available=True
    )
    db.add(new_donor)
    await db.commit()
    await db.refresh(new_donor)
    return {"message": "Success", "id": str(new_donor.id)}

@router.post("/donors/emergency")
async def emergency_blood_alert(blood_group: str, district_id: int, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    query = select(BloodDonor).where(BloodDonor.blood_group == blood_group, BloodDonor.district_id == district_id, BloodDonor.is_available == True)
    result = await db.execute(query)
    donors = result.scalars().all()
    
    message = f"URGENT: {blood_group} blood required in your district. Please contact TVK Blood Network immediately."
    
    count = 0
    for donor in donors:
        background_tasks.add_task(send_sms, donor.phone, message)
        count += 1
        
    return {"message": f"Alert sent to {count} donors."}

@router.get("/welfare")
async def get_welfare_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WelfareRequest))
    requests = result.scalars().all()
    return [{"id": r.id, "category": r.category, "status": r.status, "citizen_name": r.citizen_name} for r in requests]
