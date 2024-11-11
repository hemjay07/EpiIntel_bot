# app/services/bot.py
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from ..config import settings
import logging
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WhatsAppBot:
    def __init__(self):
        """Initialize WhatsApp bot with Twilio credentials"""
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER

    async def process_message(self, message: str) -> Tuple[str, Dict]:
        """
        Process incoming WhatsApp message and return appropriate response
        Returns: (message_text, response_data)
        """
        try:
            # Normalize message
            message = message.strip().lower()
            
            # Initialize response data
            response_data = {
                "original_message": message,
                "intent": None,
                "processed": True
            }

            # Handle different message types
            if any(word in message for word in ['hi', 'hello', 'hey']):
                response_data["intent"] = "greeting"
                return self._get_greeting_message(), response_data
                
            elif 'help' in message:
                response_data["intent"] = "help"
                return self._get_help_message(), response_data
                
            elif 'emergency' in message:
                response_data["intent"] = "emergency"
                return self._get_emergency_contacts(), response_data
                
            else:
                response_data["intent"] = "unknown"
                return self._get_default_message(), response_data

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            response_data = {
                "original_message": message,
                "intent": "error",
                "error": str(e),
                "processed": False
            }
            return "Sorry, I'm having trouble understanding. Please try again.", response_data

    def _get_greeting_message(self) -> str:
        """Return greeting message"""
        return """Welcome to EpiSense! 👋

I can help you with:
1. Current disease outbreaks
2. Local risk levels
3. Prevention tips
4. Emergency contacts

What would you like to know about?"""

    def _get_help_message(self) -> str:
        """Return help message"""
        return """Here's how to use EpiSense:

📊 For Disease Updates:
- Type 'status' for current outbreaks
- Type 'cases' for latest statistics

📍 For Local Information:
- Type 'risk' followed by your state
- Example: 'risk Lagos'

🏥 For Health Information:
- Type 'prevention' for health tips
- Type 'symptoms [disease]' for specific info
- Example: 'symptoms mpox'

🆘 For Emergency:
- Type 'emergency' for NCDC contacts

Need more help? Just ask!"""

    def _get_emergency_contacts(self) -> str:
        """Return emergency contact information"""
        return """🆘 Emergency Contacts:

NCDC Toll-Free Number:
0800-970000-10

WhatsApp:
+234 708 711 0839

SMS:
Send ALERT to 08099555577

State Emergency Operations Centers:
Reply with 'emergency [state]' for specific contacts"""

    def _get_default_message(self) -> str:
        """Return default response for unknown queries"""
        return """I'm not sure how to help with that yet. 

Try these options:
- Type 'status' for current outbreaks
- Type 'risk' followed by your state
- Type 'help' for all commands
- Type 'emergency' for NCDC contacts"""

    async def send_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message using Twilio"""
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                body=message,
                to=f'whatsapp:{to_number}'
            )
            logger.info(f"Message sent successfully: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False