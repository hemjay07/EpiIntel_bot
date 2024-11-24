# EpiSense Bot Quick Start

## Launch Bot (Windows)
```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Start server
python run.py

# 3. New terminal - start ngrok
ngrok http 8000

# 4. Copy ngrok URL to Twilio webhook:
# https://[your-ngrok-url]/api/v1/webhook
```

## Test Commands
```
hi                     → Welcome
help                   → Commands list
mpox status           → Statistics
cases mpox Lagos      → Local data
risk Lagos            → Risk level
prevention            → Health tips
emergency             → Contacts
```

## Common Issues
- Bot not responding → Check server & ngrok
- No data → Check Supabase connection
- Webhook errors → Verify Twilio settings

## Important URLs
- Twilio: console.twilio.com
- Ngrok: localhost:4040
- API: localhost:8000/docs