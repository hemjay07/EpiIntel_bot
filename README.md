# EpiSense WhatsApp Bot

A WhatsApp bot for accessing disease surveillance data using Twilio and FastAPI.

## Setup & Launch Guide

### 1. Environment Setup

1. Create a virtual environment:
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your credentials:
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 2. Launch the Bot

1. Start the FastAPI server:
```bash
python run.py
```

2. In a new terminal, start ngrok:
```bash
ngrok http 8000
```

3. Copy the ngrok HTTPS URL (e.g., https://abc123.ngrok.io)

### 3. Twilio Configuration

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to Messaging → Try it → WhatsApp
3. Find "Sandbox Settings"
4. Set your webhook:
   - When a message comes in: `your_ngrok_url/api/v1/webhook`
   - Example: `https://abc123.ngrok.io/api/v1/webhook`
   - Method: POST

### 4. Testing the Bot

1. Join Twilio Sandbox:
   - Send "join <your-sandbox-code>" to your Twilio number
   - Example: "join fish-camera"

2. Test Commands:
```
hi                      → Welcome message
help                    → List of commands
mpox status            → Mpox statistics
cholera status         → Cholera statistics
cases mpox Lagos       → Lagos mpox data
cases cholera Kano     → Kano cholera data
risk Lagos             → Risk assessment
prevention             → Health tips
emergency              → NCDC contacts
```

## Important Notes

### Ngrok Sessions
- Ngrok URLs change each time you restart ngrok
- Update Twilio webhook URL after each ngrok restart
- For persistent URLs, consider ngrok paid plan

### Twilio Sandbox Limitations
- Messages expire after 24 hours
- Only works with verified numbers during testing
- Consider upgrading to Production API for full service

### Webhook Debugging
1. Check FastAPI logs:
```bash
# Look for incoming requests
tail -f fastapi.log
```

2. Check Twilio logs:
- Console → Monitor → Logs
- Check for delivery status

3. Ngrok Inspector:
- Visit http://localhost:4040
- See all requests/responses

## Common Issues & Solutions

### 1. Bot Not Responding
- Check if FastAPI server is running
- Verify ngrok is running
- Confirm webhook URL in Twilio
- Check Twilio logs for errors

### 2. Webhook Errors
- Ensure URL includes `/api/v1/webhook`
- Check for proper POST method
- Verify Twilio credentials

### 3. Database Connection
- Check Supabase credentials
- Verify table structures
- Test database queries separately

## Maintenance Commands

### Update Dependencies
```bash
pip freeze > requirements.txt
```

### Check Logs
```bash
# View FastAPI logs
tail -f fastapi.log

# View ngrok logs
tail -f ngrok.log
```

### Restart Services
```bash
# Restart FastAPI
Ctrl+C
python run.py

# Restart ngrok
Ctrl+C
ngrok http 8000
```

## Production Considerations

1. Replace ngrok with proper hosting
2. Upgrade to Twilio Production API
3. Implement proper logging
4. Add monitoring
5. Set up automated backups
6. Implement rate limiting
7. Add error tracking

## Useful Links

- [Twilio Console](https://console.twilio.com)
- [Ngrok Dashboard](https://dashboard.ngrok.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Supabase Dashboard](https://app.supabase.io)

## Support

For issues:
1. Check logs in `logs/` directory
2. Verify all environment variables
3. Test database connection
4. Check Twilio webhook settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

Remember to never commit sensitive credentials to version control!