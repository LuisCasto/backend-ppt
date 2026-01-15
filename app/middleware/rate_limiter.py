from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Configurar rate limiter usando IP del cliente
# No cargar automáticamente desde .env para evitar problemas de codificación
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    config_filename=None  # Agregar esta línea
)

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handler personalizado para errores de rate limit"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Demasiadas solicitudes",
            "message": "Has excedido el límite de solicitudes. Por favor, espera un momento.",
            "retry_after": exc.detail
        }
    )