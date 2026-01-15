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
    docs_url="/docs" if not settings.is_production else None,  # Desactivar docs en producción
    redoc_url="/redoc" if not settings.is_production else None
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS - Configuración estricta
# Permitir todos los orígenes en desarrollo, específicos en producción
cors_origins = settings.BACKEND_CORS_ORIGINS if settings.is_production else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Incluir OPTIONS para preflight
    allow_headers=["*"],  # Permitir todos los headers
    max_age=600,  # Cache preflight por 10 minutos
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    if settings.SECURITY_HEADERS_ENABLED:
        # Prevenir clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevenir MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        if settings.is_production:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Strict Transport Security (solo en producción con HTTPS)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Trusted Host Middleware (prevenir ataques de Host Header)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "*.yourdomain.com"]  # Configurar con tu dominio
    )

# Eventos de inicio y cierre
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print(f"🚀 Iniciando {settings.PROJECT_NAME}...")
    print(f"🌍 Ambiente: {settings.ENVIRONMENT}")
    
    await connect_to_mongo()
    
    # Crear índices en MongoDB para mejor performance
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
@app.get("/")
async def root():
    return {
        "message": "🎮 Bienvenido a la API de Piedra, Papel o Tijera",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "Deshabilitado en producción"
    }

# Health check
@app.get("/health")
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
    
    # En producción, no revelar detalles del error
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