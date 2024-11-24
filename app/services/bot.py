# app/services/bot.py
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .database import DiseaseDataService
from ..config import settings
import logging
from typing import Dict, Optional, Tuple
import re

class WhatsAppBot:
    def __init__(self):
        """Initialize WhatsApp bot with Twilio credentials and database service"""
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.db = DiseaseDataService()
        self.logger = logging.getLogger(__name__)

    def process_message(self, message: str) -> Tuple[str, Dict]:
        """Process incoming WhatsApp message and return appropriate response"""
        try:
            # Normalize message
            message = message.strip().lower()
            
            # Initialize response data
            response_data = {
                "original_message": message,
                "intent": None,
                "processed": True
            }

            # Check for disease status queries
            status_match = re.match(r'(mpox|cholera)\s+status', message)
            if status_match:
                disease = status_match.group(1)
                response_data["intent"] = "disease_status"
                return self._get_disease_status(disease), response_data

            # Check for state risk queries
            risk_match = re.match(r'risk\s+(\w+)', message)
            if risk_match:
                state = risk_match.group(1).title()
                response_data["intent"] = "state_risk"
                return self._get_state_risk(state), response_data

            # Check for case numbers
            cases_match = re.match(r'cases\s+(mpox|cholera)(?:\s+(\w+))?', message)
            if cases_match:
                disease, state = cases_match.groups()
                response_data["intent"] = "case_numbers"
                if state:
                    return self._get_state_cases(disease, state.title()), response_data
                return self._get_disease_status(disease), response_data

            # Check for prevention info
            prevention_match = re.match(r'prevention(?:\s+(mpox|cholera))?', message)
            if prevention_match:
                disease = prevention_match.group(1) if prevention_match.group(1) else 'general'
                response_data["intent"] = "prevention"
                return self._get_prevention_info(disease), response_data

            # Handle basic commands
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
            self.logger.error(f"Error processing message: {str(e)}")
            response_data = {
                "original_message": message,
                "intent": "error",
                "error": str(e),
                "processed": False
            }
            return "Sorry, I'm having trouble understanding. Please try again.", response_data

    def _get_disease_status(self, disease: str) -> str:
        """Get current status for a disease"""
        summary = self.db.get_disease_summary(disease)
        rankings = self.db.get_state_rankings(disease, limit=3)
        
        if not summary:
            return f"Sorry, I couldn't find current data for {disease}."
        
        if disease == 'mpox':
            response = f"""Current MPOX Situation (Week {summary['reporting_week']}, {summary['reporting_year']}):

This Week:
📊 Confirmed Cases: {summary['weekly']['confirmed_cases']}
🔍 Suspected Cases: {summary['weekly']['suspected_cases']}
⚠️ Deaths: {summary['weekly']['deaths']}
🏥 Co-infections: {summary['weekly']['coinfection_cases']}

Total Statistics:
📈 Total Confirmed: {summary['cumulative']['confirmed_cases']}
👥 Total Suspected: {summary['cumulative']['suspected_cases']}
⚡ Gender Distribution: {summary['cumulative']['male_cases']} males, {summary['cumulative']['female_cases']} females
🗺️ Affected Areas: {summary['cumulative']['states_affected']}"""

        else:  # cholera
            response = f"""Current CHOLERA Situation (Week {summary['reporting_week']}, {summary['reporting_year']}):

This Week:
📊 Suspected Cases: {summary['weekly']['suspected_cases']}
⚠️ Deaths: {summary['weekly']['deaths']}
📉 Case Fatality Rate: {summary['weekly']['cfr']}%

Total Statistics:
📈 Total Cases: {summary['cumulative']['suspected_cases']:,}
⚡ Total Deaths: {summary['cumulative']['deaths']}
📊 Overall CFR: {summary['cumulative']['cfr']}%"""

        if rankings:
            response += "\n\nMost Affected States:"
            for rank in rankings:
                response += f"\n{rank['rank']}. {rank['state']} ({rank['percentage']}% of cases)"

        response += "\n\nReply with:"
        response += f"\n- 'cases {disease} [state]' for state details"
        response += "\n- 'prevention' for safety measures"
        
        return response

    
    def _get_state_cases(self, disease: str, state: str) -> str:
        """Get case numbers for a specific state"""
        data = self.db.get_state_data(disease, state)
        
        if not data:
            return f"Sorry, I couldn't find current {disease} data for {state}."
                
        response = f"""{disease.upper()} in {state} (Week {data['reporting_week']}, {data['reporting_year']}):"""

        # Access state-specific weekly stats
        if disease == 'mpox':
            weekly = data.get('weekly_state_stats', {}).get(state, {})
            cumulative = data.get('cumulative_state_stats', {}).get(state, {})
            
            response += "\n\nThis Week:"
            response += f"\n📊 Confirmed Cases: {weekly.get('confirmed_cases', 0)}"
            response += f"\n🔍 Suspected Cases: {weekly.get('suspected_cases', 0)}"
            
            if cumulative:
                response += "\n\nTotal Statistics:"
                response += f"\n📈 Total Cases: {cumulative.get('confirmed_cases', 0)}"
        else:  # cholera
            weekly = data.get('weekly_state_stats', {}).get(state, {})
            cumulative = data.get('cumulative_state_stats', {}).get(state, {})
            
            response += "\n\nThis Week:"
            response += f"\n📊 Suspected Cases: {weekly.get('suspected_cases', 0)}"
            response += f"\n⚠️ Deaths: {weekly.get('deaths', 0)}"
            
            if cumulative:
                response += "\n\nTotal Statistics:"
                response += f"\n📈 Total Cases: {cumulative.get('suspected_cases', 0)}"
                response += f"\n⚡ Total Deaths: {cumulative.get('deaths', 0)}"

        # Add ranking if available
        if data.get('ranking'):
            response += f"\n\n🏆 State Ranking: #{data['ranking']['rank']}"
            response += f"\n📊 {data['ranking']['percentage']}% of national cases"

        response += "\n\nReply with:"
        response += "\n• 'prevention' for safety measures"
        response += "\n• 'emergency' for contacts"
        
        return response

    def _get_state_risk(self, state: str) -> str:
        """Get current risk levels for all diseases in a state"""
        mpox_data = self.db.get_state_data('mpox', state)
        cholera_data = self.db.get_state_data('cholera', state)

        response = f"""Disease Risk Levels in {state}:"""

        if mpox_data and mpox_data.get('weekly'):
            mpox_weekly = mpox_data['weekly']
            response += "\n\nMPOX:"
            response += f"\n📊 Weekly Cases: {mpox_weekly.get('confirmed_cases', 0)} confirmed"
            if 'ranking' in mpox_data:
                response += f"\n🏆 State Ranking: #{mpox_data['ranking']['rank']}"

        if cholera_data and cholera_data.get('weekly'):
            cholera_weekly = cholera_data['weekly']
            response += "\n\nCHOLERA:"
            response += f"\n📊 Weekly Cases: {cholera_weekly.get('suspected_cases', 0)}"
            if 'ranking' in cholera_data:
                response += f"\n🏆 State Ranking: #{cholera_data['ranking']['rank']}"

        response += "\n\nReply with:"
        response += "\n- 'cases mpox/cholera " + state + "' for details"
        response += "\n- 'prevention' for safety measures"

        return response

    def _get_prevention_info(self, disease: str) -> str:
        """Get prevention information"""
        if disease == 'mpox':
            return """MPOX Prevention Tips:

1. Avoid close contact with people who have a rash
2. Avoid contact with objects used by someone with mpox
3. Wash hands often with soap and water
4. Practice safe sex and use protection
5. Watch for symptoms and isolate if they appear

Common Symptoms:
- Fever and headache
- Muscle aches
- Rash or skin lesions
- Swollen lymph nodes

Reply with 'emergency' for NCDC contacts."""

        elif disease == 'cholera':
            return """CHOLERA Prevention Tips:

1. Drink and use safe water:
   - Boil or treat water
   - Keep water in a clean, covered container

2. Practice good hygiene:
   - Wash hands with soap and safe water
   - Use latrines or proper toilets

3. Food safety:
   - Cook food thoroughly
   - Eat food while it's hot
   - Wash fruits and vegetables with safe water

Common Symptoms:
- Watery diarrhea
- Dehydration
- Vomiting

Seek immediate medical care if symptoms appear!

Reply with 'emergency' for NCDC contacts."""

        else:
            return """General Disease Prevention Tips:

1. Practice good hygiene:
   - Regular hand washing
   - Use clean water and soap
   - Cover mouth when coughing

2. Environmental hygiene:
   - Keep surroundings clean
   - Proper waste disposal
   - Good ventilation

3. Health practices:
   - Get vaccinated when available
   - Seek early medical care
   - Follow medical advice

Reply with:
- 'prevention mpox' for mpox tips
- 'prevention cholera' for cholera tips
- 'emergency' for NCDC contacts"""

    def _get_greeting_message(self) -> str:
        """Return greeting message"""
        return """Welcome to EpiSense! 👋

I can help you with:
1. Disease Updates:
   - 'mpox status'
   - 'cholera status'

2. Local Information:
   - 'risk [state]'
   - 'cases mpox Lagos'

3. Health Information:
   - 'prevention mpox'
   - 'prevention cholera'

4. Emergency Help:
   - 'emergency'

What would you like to know about?"""

    def _get_help_message(self) -> str:
        """Return help message"""
        return """How to use EpiSense:

📊 Disease Updates:
- '[disease] status' for current situation
  Example: 'mpox status'

📍 Local Information:
- 'risk [state]' for risk levels
- 'cases [disease] [state]' for numbers
  Example: 'cases mpox Lagos'

🏥 Health Information:
- 'prevention [disease]' for safety tips
  Example: 'prevention cholera'

🆘 Emergency:
- 'emergency' for NCDC contacts

Need more help? Just ask!"""

    def _get_emergency_contacts(self) -> str:
        """Return emergency contact information"""
        return """🆘 NCDC Emergency Contacts:

📞 Toll-Free Number:
6232 (All Networks)

📱 WhatsApp:
07087110839

📱 SMS:
08099555577

📧 Email:
info@ncdc.gov.ng

Reply with:
- 'prevention' for safety tips
- '[disease] status' for updates"""

    def _get_default_message(self) -> str:
        """Return default response for unknown queries"""
        return """I'm not sure how to help with that.

Try these options:
- 'mpox status' or 'cholera status'
- 'risk [state]' for local risk
- 'cases mpox Lagos' for state data
- 'help' for all commands"""

    def send_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message using Twilio"""
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                body=message,
                to=f'whatsapp:{to_number}'
            )
            self.logger.info(f"Message sent successfully: {message.sid}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False