from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.domain import UserRole, WorkStatus, Priority

# Base Config
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(ORMModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# District & Ward Schemas
class DistrictBase(ORMModel):
    name: str

class DistrictResponse(DistrictBase):
    id: int

class WardBase(ORMModel):
    ward_number: str
    district_id: int
    councillor_id: Optional[UUID] = None

class WardResponse(WardBase):
    id: int

# Work Order Schemas
class WorkOrderBase(ORMModel):
    title: str
    description: Optional[str] = None
    category: str
    status: WorkStatus = WorkStatus.pending
    ward_id: int
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    budget_sanctioned: Optional[float] = 0.0
    responsibility: Optional[str] = "Ward Councillor Office"

class WorkOrderCreate(WorkOrderBase):
    pass

class WorkOrderResponse(WorkOrderBase):
    id: UUID
    councillor_id: UUID
    created_at: datetime
    updated_at: datetime

# Complaint Schemas
class ComplaintBase(ORMModel):
    description: str
    category: Optional[str] = None
    priority: Priority = Priority.low
    photo_url: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    location_address: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintResponse(ComplaintBase):
    id: UUID
    ward_id: Optional[int]
    councillor_id: Optional[UUID]
    status: WorkStatus
    is_ai_triaged: bool
    created_at: datetime

# Volunteer Schemas
class VolunteerBase(ORMModel):
    full_name: str
    dob: datetime
    phone: str
    email: Optional[EmailStr] = None
    district_id: int
    block: Optional[str] = None
    booth_number: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_url: Optional[str] = None
    is_approved: Optional[bool] = False

class VolunteerCreate(VolunteerBase):
    pass

class VolunteerResponse(VolunteerBase):
    id: UUID
    membership_id: str
    qr_code_url: Optional[str]
    card_url: Optional[str]
    created_at: datetime

class VolunteerPostBase(ORMModel):
    description: str
    photo_url: Optional[str] = None

class VolunteerPostCreate(VolunteerPostBase):
    pass

class VolunteerPostResponse(VolunteerPostBase):
    id: UUID
    volunteer_id: UUID
    created_at: datetime

# Charity Schemas
class CharityCampaignBase(ORMModel):
    title: str
    type_emoji: str
    district_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    target_beneficiaries: int

class CharityCampaignResponse(CharityCampaignBase):
    id: UUID
    current_beneficiaries: int
