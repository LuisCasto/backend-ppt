from fastapi import APIRouter, HTTPException, Request
from app.schemas.game_schemas import PlayRequest, PlayResponse
from app.services.game_logic import GameLogic
from app.middleware.rate_limiter import limiter
from app.config import settings

router = APIRouter(
    prefix="/game",
    tags=["game"]
)

@router.post("/play", response_model=PlayResponse)
@limiter.limit(f"{settings.MAX_GAME_PLAYS_PER_MINUTE}/minute")
async def play_round(request: Request, play_request: PlayRequest):
    """
    Realizar una jugada contra la computadora
    
    Rate limit: 30 jugadas por minuto por IP
    """
    try:
        # Validación adicional de seguridad
        if play_request.player_move not in settings.ALLOWED_MOVES:
            raise HTTPException(
                status_code=400, 
                detail="Movimiento inválido"
            )
        
        if play_request.mode not in settings.ALLOWED_GAME_MODES:
            raise HTTPException(
                status_code=400, 
                detail="Modo de juego inválido"
            )
        
        # Obtener jugada de la CPU según el modo
        if play_request.mode == "normal":
            cpu_move = GameLogic.get_cpu_move_normal()
        else:  # imposible
            cpu_move = GameLogic.get_cpu_move_imposible(play_request.player_move)
        
        # Evaluar resultado
        result = GameLogic.evaluate_round(play_request.player_move, cpu_move)
        
        return PlayResponse(
            cpu_move=cpu_move,
            result=result
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        print(f"Error en play_round: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor"
        )