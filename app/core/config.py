import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Production settings
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    def get_db_url(self) -> str:
        return self.database_url

# Auto-detect production environment
if os.getenv("RENDER"):
    # Running on Render
    settings = Settings(
        environment="production",
        debug=False,
        access_token_expire_minutes=30  # Shorter tokens in production
    )
else:
    settings = Settings()