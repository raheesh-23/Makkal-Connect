from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any
import asyncio

from app.core.database import get_db
from app.models.domain import WorkOrder, Complaint, Ward, WorkStatus, User, UserRole, District
from app.schemas.domain import WorkOrderCreate, WorkOrderResponse, ComplaintCreate, ComplaintResponse
from app.api.v1.auth import get_current_user
from app.services.ai_triage import classify_complaint_sync

router = APIRouter()

@router.get("/districts", response_model=List[dict])
async def get_districts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(District))
    districts = result.scalars().all()
    return [{"id": d.id, "name": d.name} for d in districts]

@router.get("/wards", response_model=List[dict])
async def get_wards(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ward))
    wards = result.scalars().all()
    return [{"id": w.id, "ward_number": w.ward_number, "district_id": w.district_id} for w in wards]

@router.get("/orders", response_model=List[WorkOrderResponse])
async def get_work_orders(ward_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(WorkOrder)
    if ward_id:
        query = query.where(WorkOrder.ward_id == ward_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/orders", response_model=WorkOrderResponse)
async def create_work_order(order_in: WorkOrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = WorkOrder(**order_in.model_dump(), councillor_id=current_user.id)
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

@router.patch("/orders/{id}", response_model=WorkOrderResponse)
async def update_work_order(id: str, order_in: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    import uuid
    result = await db.execute(select(WorkOrder).where(WorkOrder.id == uuid.UUID(id)))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
        
    if "status" in order_in:
        order.status = order_in["status"]
    if "budget_sanctioned" in order_in:
        order.budget_sanctioned = float(order_in["budget_sanctioned"])
    if "responsibility" in order_in:
        order.responsibility = order_in["responsibility"]
        
    await db.commit()
    await db.refresh(order)
    return order

@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(complaint_in: ComplaintCreate, db: AsyncSession = Depends(get_db)):
    complaint = Complaint(**complaint_in.model_dump(exclude_unset=True))
    
    # Run AI triage asynchronously
    loop = asyncio.get_event_loop()
    triage_result = await loop.run_in_executor(None, classify_complaint_sync, complaint.description)
    
    complaint.category = triage_result.get("category", "General")
    complaint.priority = triage_result.get("priority", "LOW")
    complaint.is_ai_triaged = True
    
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)
    return complaint

@router.get("/complaints", response_model=List[ComplaintResponse])
async def get_complaints(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Complaint))
    return result.scalars().all()

@router.patch("/complaints/{id}/verify", response_model=ComplaintResponse)
async def verify_complaint(id: str, verify: bool, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if admin or councillor
    if current_user.role not in [UserRole.admin, UserRole.councillor]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    import uuid
    result = await db.execute(select(Complaint).where(Complaint.id == uuid.UUID(id)))
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = WorkStatus.verified if verify else WorkStatus.completed
    await db.commit()
    await db.refresh(complaint)
    return complaint
@router.get("/stats")
async def get_work_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkOrder))
    orders = result.scalars().all()
    total = len(orders)
    completed = sum(1 for o in orders if o.status in (WorkStatus.completed, WorkStatus.verified))
    return {
        "total_orders": total,
        "completion_rate": (completed / total * 100) if total > 0 else 0,
        "completed": completed
    }
