# app/routes/webhook.py
from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from ..services.bot import WhatsAppBot
import logging
from typing import Optional

router = APIRouter()
bot = WhatsAppBot()
logger = logging.getLogger(__name__)

@router.post("/webhook")
async def webhook_handler(
    Body: str = Form(...),
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None)
):
    """Handle incoming WhatsApp messages"""
    try:
        # Log incoming message
        logger.info(f"Incoming message - From: {From}, Body: {Body}")
        
        # Process the message
        response_text, response_data = await bot.process_message(Body)
        
        # Log the response we're about to send
        logger.info(f"Sending response: {response_text}")
        
        # Create TwiML response - this is what Twilio expects
        resp = MessagingResponse()
        resp.message(response_text)
        
        # Return response in the format Twilio expects
        return Response(
            content=str(resp),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again later.")
        return Response(
            content=str(resp),
            media_type="application/xml"
        )