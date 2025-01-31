from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    OAUTH2_CLIENT_ID: str
    OAUTH2_CLIENT_SECRET: str
    OAUTH2_METADATA_URL: str
    POSTGRES_DB: str
    RABBITMQ_HOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    STRIPE_API_KEY: str
    class Config:
        env_file = None if os.getenv('HOSTING_ENVIRONMENT') == 'Production' else '.env'

settings = Settings()