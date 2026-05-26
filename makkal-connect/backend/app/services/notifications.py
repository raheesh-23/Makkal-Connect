from twilio.rest import Client
from app.core.config import settings

def send_sms(to_number: str, message_body: str) -> bool:
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print(f"Mock SMS to {to_number}: {message_body}")
        return True
        
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number
        )
        return True
    except Exception as e:
        print(f"Twilio Error: {e}")
        return False
