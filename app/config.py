from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Database - PostgreSQL by default
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://canteen_user:canteen_pass@localhost:5432/canteen_db"
    )
    
    # JWT Settings
    JWT_SECRET: str = 'supersecret'
    JWT_ALGORITHM: str = 'HS256'

    class Config:
        env_file = '.env'


settings = Settings()
