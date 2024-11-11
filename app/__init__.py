# app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import webhook
import logging

logger = logging.getLogger(__name__)

def create_app():
    app = FastAPI(
        title="WhatsApp Bot",
        description="WhatsApp bot for disease surveillance",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(webhook.router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting WhatsApp bot service...")

    return app