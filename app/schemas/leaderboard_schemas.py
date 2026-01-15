from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re
from app.config import settings

class LeaderboardEntry(BaseModel):
    player_name: str = Field(
        ..., 
        min_length=settings.MIN_PLAYER_NAME_LENGTH,
        max_length=settings.MAX_PLAYER_NAME_LENGTH,
        description="Nombre del jugador (1-5 caracteres)"
    )
    score: int = Field(
        ..., 
        ge=-500, 
        le=500,
        description="Puntuación del jugador"
    )
    mode: str = Field(
        ..., 
        pattern="^(normal|imposible)$",
        description="Modo de juego"
    )
    timestamp: Optional[datetime] = None
    
    @field_validator('player_name')
    @classmethod
    def sanitize_player_name(cls, v):
        # Remover espacios al inicio y final
        v = v.strip()
        
        # Validar longitud
        if len(v) < settings.MIN_PLAYER_NAME_LENGTH:
            raise ValueError(f'Nombre muy corto. Mínimo {settings.MIN_PLAYER_NAME_LENGTH} carácter')
        if len(v) > settings.MAX_PLAYER_NAME_LENGTH:
            raise ValueError(f'Nombre muy largo. Máximo {settings.MAX_PLAYER_NAME_LENGTH} caracteres')
        
        # Permitir solo letras, números y algunos caracteres especiales seguros
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Nombre contiene caracteres inválidos. Solo se permiten letras, números, guiones y guiones bajos')
        
        # Convertir a mayúsculas
        return v.upper()
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        v = v.lower().strip()
        if v not in settings.ALLOWED_GAME_MODES:
            raise ValueError(f'Modo inválido. Debe ser uno de: {settings.ALLOWED_GAME_MODES}')
        return v
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v):
        # Validar que el score esté en un rango razonable
        # Máximo: 5 victorias = 500, Mínimo: 5 derrotas = -500
        if v < -500 or v > 500:
            raise ValueError('Puntuación fuera de rango válido')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_name": "LUIS",
                "score": 300,
                "mode": "normal"
            }
        }

class LeaderboardResponse(BaseModel):
    player_name: str = Field(..., description="Nombre del jugador")
    score: int = Field(..., description="Puntuación")
    timestamp: datetime = Field(..., description="Fecha y hora del registro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_name": "LUIS",
                "score": 300,
                "timestamp": "2025-01-05T12:00:00"
            }
        }