# Makkal Connect 🌟
TVK Digital Governance Platform

## Features
- **Module 1**: Councillor Work Status (Interactive Map, Complaints, AI Triage)
- **Module 2**: Singapadai Volunteer Management (Registration, Digital ID generation)
- **Module 3**: Charity & Welfare Portal (Campaigns tracking, Blood Donor Network with SMS alerts)

## Tech Stack
- Frontend: Streamlit (Python only, fully custom styled)
- Backend: FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL, Redis
- Services: Anthropic API, Twilio SMS API

## Running Locally

1. Create a `.env` file in the root based on `.env.example`.
2. Ensure Docker and Docker Compose are installed.
3. Start the services:
   ```bash
   docker-compose up --build -d
   ```
4. Access the applications:
   - **Frontend**: http://localhost:8501
   - **Backend API Docs**: http://localhost:8000/docs
5. Run the seed data script (inside the api container):
   ```bash
   docker-compose exec api python ../seed_data.py
   ```

## Development
- All code is strictly Python without JavaScript frameworks.
- Tailwind/JS are avoided. Custom CSS ensures the UI matches the TVK brand (Deep Navy and Gold).
