from fastapi import APIRouter, HTTPException, Request
from typing import List
from app.schemas.leaderboard_schemas import LeaderboardEntry, LeaderboardResponse
from app.services.database import save_leaderboard_entry, get_leaderboard
from app.middleware.rate_limiter import limiter
from app.config import settings

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"]
)

@router.get("/{mode}", response_model=List[LeaderboardResponse])
@limiter.limit(f"{settings.MAX_REQUESTS_PER_MINUTE}/minute")
async def get_leaderboard_by_mode(request: Request, mode: str):
    """
    Obtener el top 10 del leaderboard según el modo
    
    Rate limit: 60 solicitudes por minuto por IP
    """
    # Sanitizar y validar modo
    mode = mode.lower().strip()
    
    if mode not in settings.ALLOWED_GAME_MODES:
        raise HTTPException(
            status_code=400, 
            detail=f"Modo inválido. Debe ser uno de: {', '.join(settings.ALLOWED_GAME_MODES)}"
        )
    
    try:
        entries = await get_leaderboard(mode, limit=10)
        return entries
    except Exception as e:
        print(f"Error obteniendo leaderboard: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor"
        )

@router.post("/", status_code=201)
@limiter.limit(f"{settings.MAX_LEADERBOARD_SAVES_PER_MINUTE}/minute")
async def save_score(request: Request, entry: LeaderboardEntry):
    """
    Guardar puntuación en el leaderboard
    
    Rate limit: 10 guardados por minuto por IP
    """
    try:
        # La validación y sanitización ya se hace en el schema LeaderboardEntry
        result = await save_leaderboard_entry(
            player_name=entry.player_name,
            score=entry.score,
            mode=entry.mode
        )
        
        return {
            "message": "Puntuación guardada exitosamente",
            "id": str(result),
            "player_name": entry.player_name,
            "score": entry.score
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error guardando puntuación: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor"
        )