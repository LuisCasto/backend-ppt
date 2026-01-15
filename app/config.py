from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # MongoDB - CRÍTICO: Nunca exponer en código
    MONGODB_URI: str
    DATABASE_NAME: str = "ppt_game"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Piedra Papel Tijera API"
    
    # CORS - Configurar según ambiente
    ENVIRONMENT: str = "development"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_GAME_PLAYS_PER_MINUTE: int = 30
    MAX_LEADERBOARD_SAVES_PER_MINUTE: int = 10
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = True
    
    # Input Validation
    MAX_PLAYER_NAME_LENGTH: int = 5
    MIN_PLAYER_NAME_LENGTH: int = 1
    ALLOWED_GAME_MODES: List[str] = ["normal", "imposible"]
    ALLOWED_MOVES: List[int] = [1, 2, 3]
    
    # MongoDB Indexes
    CREATE_INDEXES_ON_STARTUP: bool = True
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'

settings = Settings()