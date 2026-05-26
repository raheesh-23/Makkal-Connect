import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.models.domain import District, Ward, WorkOrder, CharityCampaign, Volunteer, Base, User, UserRole, BloodDonor
from app.core.security import get_password_hash

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/makkal_connect")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

def utcnow():
    return datetime.now(timezone.utc)

async def seed():
    async with engine.begin() as conn:
        from sqlalchemy import text
        print("Dropping existing tables for a clean schema upgrade...")
        try:
            await conn.execute(text("DROP TABLE IF EXISTS work_evidence, work_orders, complaints, volunteers, wards, districts, charity_campaigns, users CASCADE"))
        except Exception as e:
            print(f"Drop failed: {e}")
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        from sqlalchemy import text
        print("Clearing existing data for a fresh seed...")
        try:
            await session.execute(text("TRUNCATE TABLE districts, wards, work_orders, charity_campaigns, volunteers, users CASCADE"))
            await session.commit()
        except Exception as e:
            print(f"Clear skipped: {e}")

        print("Seeding districts...")
        tn_districts = [
            "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
            "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
            "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
            "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
            "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
            "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
            "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
            "Vellore", "Viluppuram", "Virudhunagar"
        ]
        districts = [
            District(id=i+1, name=name) for i, name in enumerate(tn_districts)
        ]
        session.add_all(districts)
        
        print("Seeding admin user...")
        admin = User(
            id=uuid.uuid4(),
            email="admin@tvk.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin",
            role=UserRole.admin
        )
        session.add(admin)

        print("Seeding councillor user...")
        councillor = User(
            id=uuid.uuid4(),
            email="councillor@tvk.com",
            hashed_password=get_password_hash("councillor123"),
            full_name="V. S. Mani",
            role=UserRole.councillor
        )
        session.add(councillor)

        print("Seeding wards & work orders...")
        for i in range(1, 11):
            ward = Ward(ward_number=f"W{i}", district_id=1, councillor_id=councillor.id)
            session.add(ward)
            await session.flush()
            
            wo1 = WorkOrder(
                title=f"Fix Road in W{i}", category="Roads", status="Pending", 
                ward_id=ward.id, councillor_id=councillor.id, gps_lat=13.0827 + i*0.01, gps_lng=80.2707,
                budget_sanctioned=450000.0 + i*15000.0, responsibility="Highways Department"
            )
            wo2 = WorkOrder(
                title=f"Streetlight Repair W{i}", category="Electricity", status="Completed", 
                ward_id=ward.id, councillor_id=councillor.id, gps_lat=13.0927 + i*0.01, gps_lng=80.2807,
                budget_sanctioned=120000.0, responsibility="City Corporation Electrical Division"
            )
            session.add_all([wo1, wo2])

        print("Seeding charity campaigns...")
        campaigns = [
            CharityCampaign(title="Mega Blood Camp", type_emoji="🩸", district_id=1, start_date=utcnow(), target_beneficiaries=1000, current_beneficiaries=250),
            CharityCampaign(title="Food Drive", type_emoji="🍛", district_id=2, start_date=utcnow(), target_beneficiaries=500, current_beneficiaries=150)
        ]
        session.add_all(campaigns)
        
        print("Seeding blood donors...")
        donors = [
            BloodDonor(name="Karthik Raja", blood_group="O+", district_id=1, phone="9876543210", is_available=True),
            BloodDonor(name="Vijay Kumar", blood_group="A+", district_id=1, phone="8765432109", is_available=True),
            BloodDonor(name="Aishwarya Sen", blood_group="O+", district_id=1, phone="7654321098", is_available=True)
        ]
        session.add_all(donors)
        
        await session.commit()
        print("Seed complete.")

if __name__ == "__main__":
    asyncio.run(seed())
