from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.services.database import connect_to_mongo, close_mongo_connection
from app.routes import game, leaderboard
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para el juego Piedra, Papel o Tijera",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS - Configuración estricta
cors_origins = settings.BACKEND_CORS_ORIGINS if settings.is_production else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes por ahora
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    if settings.SECURITY_HEADERS_ENABLED:
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CSP más permisivo en producción para evitar problemas
        if settings.is_production:
            response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' *"
        
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Trusted Host Middleware - DESHABILITADO para evitar bloqueos
# Configurar solo cuando tengas dominio personalizado
# if settings.is_production:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=["backend-ppt-p0w6.onrender.com", "*.onrender.com"]
#     )

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print(f"🚀 Iniciando {settings.PROJECT_NAME}...")
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    
    await connect_to_mongo()
    
    if settings.CREATE_INDEXES_ON_STARTUP:
        from app.services.database import create_indexes
        await create_indexes()
    
    print("✅ Aplicación lista")

@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    await close_mongo_connection()

# Registrar routers
app.include_router(game.router, prefix=settings.API_V1_STR)
app.include_router(leaderboard.router, prefix=settings.API_V1_STR)

# Ruta raíz
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "🎮 Bienvenido a la API de Piedra, Papel o Tijera",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "api_prefix": settings.API_V1_STR,
        "health_check": "/health",
        "documentation": "/docs" if not settings.is_production else "Deshabilitado en producción"
    }

# Ruta de bienvenida de la API
@app.get("/api", tags=["root"])
@app.get("/api/", tags=["root"])
async def api_root():
    return {
        "message": "🎮 API de Piedra, Papel o Tijera",
        "version": "1.0.0",
        "endpoints": {
            "game": "/api/game/play",
            "leaderboard_normal": "/api/leaderboard/normal",
            "leaderboard_imposible": "/api/leaderboard/imposible",
            "save_score": "/api/leaderboard"
        }
    }

# Health check
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para excepciones no capturadas"""
    print(f"❌ Error no capturado: {str(exc)}")
    
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={"error": "Error interno del servidor"}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error interno del servidor",
                "detail": str(exc)
            }
        )