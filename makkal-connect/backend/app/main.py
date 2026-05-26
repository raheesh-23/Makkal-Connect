from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import auth, works, volunteers, charity, dashboard
from app.core.database import engine, AsyncSessionLocal
from app.models.domain import Base, User, UserRole, District, Ward, WorkOrder, CharityCampaign, BloodDonor
from app.core.security import get_password_hash
import uuid
from datetime import datetime, timezone
from sqlalchemy import select

def utcnow():
    return datetime.now(timezone.utc)

async def init_db():
    # 1. Create tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Check if we need to seed
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalars().first()
        if not user:
            print("No users found. Seeding initial data...")
            # Seed districts
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
            
            # Seed admin user
            admin = User(
                id=uuid.uuid4(),
                email="admin@tvk.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin",
                role=UserRole.admin
            )
            session.add(admin)

            # Seed councillor user
            councillor = User(
                id=uuid.uuid4(),
                email="councillor@tvk.com",
                hashed_password=get_password_hash("councillor123"),
                full_name="V. S. Mani",
                role=UserRole.councillor
            )
            session.add(councillor)
            await session.flush()

            # Seed wards & work orders
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

            # Seed charity campaigns
            campaigns = [
                CharityCampaign(title="Mega Blood Camp", type_emoji="🩸", district_id=1, start_date=utcnow(), target_beneficiaries=1000, current_beneficiaries=250),
                CharityCampaign(title="Food Drive", type_emoji="🍛", district_id=2, start_date=utcnow(), target_beneficiaries=500, current_beneficiaries=150)
            ]
            session.add_all(campaigns)
            
            # Seed blood donors
            donors = [
                BloodDonor(name="Karthik Raja", blood_group="O+", district_id=1, phone="9876543210", is_available=True),
                BloodDonor(name="Vijay Kumar", blood_group="A+", district_id=1, phone="8765432109", is_available=True),
                BloodDonor(name="Aishwarya Sen", blood_group="O+", district_id=1, phone="7654321098", is_available=True)
            ]
            session.add_all(donors)
            
            await session.commit()
            print("Database seeding completed on startup.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        print(f"Error during db initialization: {e}")
    yield

app = FastAPI(title="Makkal Connect API", lifespan=lifespan)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(works.router, prefix="/api/v1/works", tags=["Works"])
app.include_router(volunteers.router, prefix="/api/v1/volunteers", tags=["Volunteers"])
app.include_router(charity.router, prefix="/api/v1/charity", tags=["Charity"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Welcome to Makkal Connect API"}
