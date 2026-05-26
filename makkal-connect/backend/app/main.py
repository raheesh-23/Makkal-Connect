from fastapi import FastAPI
from app.api.v1 import auth, works, volunteers, charity, dashboard

app = FastAPI(title="Makkal Connect API")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(works.router, prefix="/api/v1/works", tags=["Works"])
app.include_router(volunteers.router, prefix="/api/v1/volunteers", tags=["Volunteers"])
app.include_router(charity.router, prefix="/api/v1/charity", tags=["Charity"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Welcome to Makkal Connect API"}
