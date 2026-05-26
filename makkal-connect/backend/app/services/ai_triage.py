import anthropic
import json
from app.core.config import settings

def classify_complaint_sync(text: str) -> dict:
    if not settings.ANTHROPIC_API_KEY:
        # Mock logic
        return {"category": "General", "priority": "LOW", "ward_extracted": None}
        
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    prompt = f"""
    You are an AI assistant for a civic governance platform. 
    Analyze the following citizen complaint and output a JSON object with:
    - category (String: e.g., Water, Road, Electricity, Sanitation)
    - priority (String: LOW, MED, HIGH, URGENT)
    - ward_extracted (String or null if not mentioned)

    Complaint: "{text}"
    
    Respond ONLY with the JSON object, nothing else.
    """
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content[0].text)
    except Exception as e:
        print(f"AI Triage Error: {e}")
        return {"category": "Unknown", "priority": "LOW", "ward_extracted": None}
