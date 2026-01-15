from pydantic import BaseModel, Field, field_validator
from app.config import settings

class PlayRequest(BaseModel):
    player_move: int = Field(
        ..., 
        ge=1, 
        le=3, 
        description="1=Piedra, 2=Papel, 3=Tijera"
    )
    mode: str = Field(
        ..., 
        pattern="^(normal|imposible)$",
        description="Modo de juego: normal o imposible"
    )
    
    @field_validator('player_move')
    @classmethod
    def validate_move(cls, v):
        if v not in settings.ALLOWED_MOVES:
            raise ValueError(f'Movimiento inválido. Debe ser uno de: {settings.ALLOWED_MOVES}')
        return v
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        v = v.lower().strip()
        if v not in settings.ALLOWED_GAME_MODES:
            raise ValueError(f'Modo inválido. Debe ser uno de: {settings.ALLOWED_GAME_MODES}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "player_move": 1,
                "mode": "normal"
            }
        }

class PlayResponse(BaseModel):
    cpu_move: int = Field(..., ge=1, le=3, description="Movimiento de la CPU")
    result: str = Field(..., pattern="^(player|cpu|tie)$", description="Resultado de la ronda")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cpu_move": 2,
                "result": "cpu"
            }
        }