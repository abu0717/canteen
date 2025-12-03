from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = 'sqlite:///./test.db'
    JWT_SECRET: str = 'supersecret'
    JWT_ALGORITHM: str = 'HS256'

    class Config:
        env_file = '.env'


settings = Settings()
