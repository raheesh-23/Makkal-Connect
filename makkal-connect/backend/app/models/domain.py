import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

def utcnow():
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    admin = "admin"
    leadership = "leadership"
    councillor = "councillor"
    district_coordinator = "district_coordinator"
    volunteer = "volunteer"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    wards = relationship("Ward", back_populates="district")

class Ward(Base):
    __tablename__ = "wards"
    id = Column(Integer, primary_key=True, index=True)
    ward_number = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), index=True, nullable=False)
    councillor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    district = relationship("District", back_populates="wards")
    councillor = relationship("User")

class WorkStatus(str, enum.Enum):
    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"
    verified = "Verified"

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)
    status = Column(Enum(WorkStatus), default=WorkStatus.pending, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), index=True, nullable=False)
    councillor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    budget_sanctioned = Column(Float, nullable=True, default=0.0)
    responsibility = Column(String, nullable=True, default="Ward Councillor Office")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class WorkEvidence(Base):
    __tablename__ = "work_evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id"), index=True, nullable=False)
    photo_url = Column(String, nullable=False)
    stage = Column(String, nullable=False) # e.g. before, during, after
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Priority(str, enum.Enum):
    low = "LOW"
    med = "MED"
    high = "HIGH"
    urgent = "URGENT"

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    priority = Column(Enum(Priority), default=Priority.low)
    ward_id = Column(Integer, ForeignKey("wards.id"), index=True, nullable=True)
    councillor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=True)
    status = Column(Enum(WorkStatus), default=WorkStatus.pending)
    is_ai_triaged = Column(Boolean, default=False)
    photo_url = Column(String, nullable=True)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    location_address = Column(String, nullable=True)
    voice_submitted = Column(Boolean, default=False)
    audio_url = Column(String, nullable=True)
    transcribed_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class VolunteerPost(Base):
    __tablename__ = "volunteer_posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), index=True, nullable=False)
    description = Column(Text, nullable=False)
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class Volunteer(Base):
    __tablename__ = "volunteers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    membership_id = Column(String, unique=True, index=True, nullable=False) # TVK-DIST-YYYY-XXXXX
    full_name = Column(String, nullable=False)
    dob = Column(DateTime(timezone=True), nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), index=True, nullable=False)
    block = Column(String, nullable=True)
    booth_number = Column(String, nullable=True)
    id_proof_type = Column(String, nullable=True)
    id_proof_url = Column(String, nullable=True)
    qr_code_url = Column(String, nullable=True)
    card_url = Column(String, nullable=True)
    reputation_score = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class Promise(Base):
    __tablename__ = "promises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    is_kept = Column(Boolean, default=False)
    councillor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class CitizenJury(Base):
    __tablename__ = "citizen_juries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    complaint_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False)
    status = Column(String, default="Reviewing") # Reviewing, Verdict_Reached
    verdict = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class VolunteerBadge(Base):
    __tablename__ = "volunteer_badges"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), index=True, nullable=False)
    badge_name = Column(String, nullable=False) # e.g., "Voter Registration Expert"
    earned_at = Column(DateTime(timezone=True), default=utcnow)

class WardStats(Base):
    __tablename__ = "ward_stats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), index=True, nullable=False)
    resolution_score = Column(Float, default=0.0)
    volunteer_turnout = Column(Integer, default=0)
    month = Column(String, nullable=False) # e.g., "2026-05"

class VolunteerRequest(Base):
    __tablename__ = "volunteer_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    councillor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    required_count = Column(Integer, default=1)
    reward_per_volunteer = Column(Integer, default=0)
    urgency = Column(String, default="medium") # low, medium, high, emergency
    status = Column(String, default="open") # open, filled, cancelled
    created_at = Column(DateTime(timezone=True), default=utcnow)

class MarketplaceAcceptance(Base):
    __tablename__ = "marketplace_acceptances"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    request_id = Column(UUID(as_uuid=True), ForeignKey("volunteer_requests.id"), index=True, nullable=False)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), index=True, nullable=False)
    status = Column(String, default="accepted") # accepted, confirmed, completed
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    venue = Column(String, nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False)
    qr_code_url = Column(String, nullable=True)
    war_room_mode = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class EventAttendance(Base):
    __tablename__ = "event_attendance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), index=True, nullable=False)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), index=True, nullable=False)
    attended = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("volunteers.id"), index=True, nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), index=True, nullable=True)
    status = Column(Enum(WorkStatus), default=WorkStatus.pending)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class CharityCampaign(Base):
    __tablename__ = "charity_campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    type_emoji = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), index=True, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    target_beneficiaries = Column(Integer, default=0)
    current_beneficiaries = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class WelfareRequest(Base):
    __tablename__ = "welfare_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    document_url = Column(String, nullable=True)
    status = Column(String, default="Submitted") # Submitted, Under Review, Approved, Fulfilled
    citizen_name = Column(String, nullable=False)
    citizen_phone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class BloodDonor(Base):
    __tablename__ = "blood_donors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    blood_group = Column(String, index=True, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), index=True, nullable=False)
    phone = Column(String, nullable=False)
    last_donated_date = Column(DateTime(timezone=True), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class CouncillorRating(Base):
    __tablename__ = "councillor_ratings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    councillor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    rating = Column(Integer, nullable=False) # 1-5
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
