from fastapi import FastAPI # type: ignore
from routers import payment_router, health_router
from database.database import engine
from models.payment_model import Base
import sys
import threading
from rabbitmq.rabbitmq_consumer import start_consumer
from sqlalchemy.exc import OperationalError # type: ignore
from sqlalchemy import inspect # type: ignore
import requests
from open_id_connect import OpenIdConnect
from env import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HotelUp payment Service",
    description="API for managing hotel payments",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.OAUTH2_CLIENT_ID,
        "clientSecret": settings.OAUTH2_CLIENT_SECRET,
        "scopes": ["openid", "email"],
        "additionalQueryStringParams": {
            "response_type": "code",
            "prompt": "login"
        }
    },
    docs_url="/api/payment/swagger",
    redoc_url="/api/payment/redoc",
    swagger_ui_oauth2_redirect_url="/api/payment/swagger/oauth2-redirect.html",
    openapi_url="/api/payment/openapi.json",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_router.router)
app.include_router(health_router.router)

# # Create database tables
# Base.metadata.create_all(bind=engine)
# Check if the database and tables exist
def check_and_create_tables():
    inspector = inspect(engine)
    if not inspector.has_table("payments", schema="payment"):
        Base.metadata.create_all(bind=engine)

# Create database tables if they do not exist
check_and_create_tables()

# Start RabbitMQ consumer
@app.on_event("startup")
def startup_event():
    start_consumer()