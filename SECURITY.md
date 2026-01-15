# 🔒 Medidas de Seguridad Implementadas

Este documento describe las medidas de seguridad implementadas siguiendo las mejores prácticas de OWASP.

## 1. Rate Limiting ⏱️

### Límites Implementados:
- **Global**: 100 solicitudes/minuto por IP
- **Endpoint /game/play**: 30 jugadas/minuto por IP
- **Endpoint /leaderboard GET**: 60 solicitudes/minuto por IP
- **Endpoint /leaderboard POST**: 10 guardados/minuto por IP

### Tecnología:
- Librería: `slowapi`
- Identificación: IP del cliente
- Respuesta 429 con mensaje informativo al exceder límites

### Configuración:
```python
# En config.py
MAX_REQUESTS_PER_MINUTE=60
MAX_GAME_PLAYS_PER_MINUTE=30
MAX_LEADERBOARD_SAVES_PER_MINUTE=10
```

---

## 2. Validación y Sanitización de Entradas 🛡️

### Validaciones en Nombres de Jugador:
- ✅ Longitud: 1-5 caracteres
- ✅ Caracteres permitidos: A-Z, 0-9, guión, guión bajo
- ✅ Conversión automática a MAYÚSCULAS
- ✅ Trim de espacios
- ❌ Prevención de inyección SQL/NoSQL
- ❌ Prevención de XSS

### Validaciones en Movimientos de Juego:
- ✅ Solo valores 1, 2, 3 (Piedra, Papel, Tijera)
- ✅ Tipo de dato entero
- ✅ Validación en schema Pydantic
- ✅ Validación adicional en endpoint

### Validaciones en Modos de Juego:
- ✅ Solo "normal" o "imposible"
- ✅ Conversión a minúsculas
- ✅ Trim de espacios
- ✅ Validación por regex

### Validaciones en Puntuaciones:
- ✅ Rango: -500 a 500
- ✅ Validación de tipo entero
- ✅ Prevención de valores absurdos

### Implementación:
```python
# Uso de Pydantic con field_validator
@field_validator('player_name')
@classmethod
def sanitize_player_name(cls, v):
    v = v.strip()
    if not re.match(r'^[a-zA-Z0-9_-]+$', v):
        raise ValueError('Caracteres inválidos')
    return v.upper()
```

---

## 3. Manejo Seguro de API Keys y Credenciales 🔑

### Variables de Entorno:
- ✅ Uso de `.env` para credenciales sensibles
- ✅ `.env` excluido de Git (`.gitignore`)
- ✅ `.env.example` como template
- ✅ `pydantic-settings` para validación

### MongoDB URI:
```python
# ❌ NUNCA hacer esto:
MONGODB_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"

# ✅ Siempre usar:
MONGODB_URI: str  # Cargado desde .env
```

### Configuración de Producción:
- Usar variables de entorno del sistema o servicio de secrets
- Rotar credenciales periódicamente
- MongoDB: Habilitar IP Whitelist
- MongoDB: Usar roles con mínimos privilegios

---

## 4. Headers de Seguridad 🛡️

### Headers HTTP Implementados:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self' (producción)
Strict-Transport-Security: max-age=31536000; includeSubDomains (producción)
```

### Propósito:
- Prevenir clickjacking
- Prevenir MIME sniffing
- Protección XSS legacy
- Control de referrer
- CSP para recursos
- HSTS para HTTPS

---

## 5. CORS (Cross-Origin Resource Sharing) 🌐

### Configuración Estricta:
```python
allow_origins=settings.BACKEND_CORS_ORIGINS  # Solo dominios autorizados
allow_methods=["GET", "POST"]  # Solo métodos necesarios
allow_headers=["Content-Type", "Authorization"]  # Headers específicos
```

### Producción:
Actualizar `BACKEND_CORS_ORIGINS` en `.env` con tu dominio real:
```bash
BACKEND_CORS_ORIGINS=["https://misitioweb.com","https://www.misitioweb.com"]
```

---

## 6. Índices de Base de Datos 📊

### MongoDB Indexes:
```python
# Optimización de consultas
score_desc: Para obtener top scores rápidamente
timestamp_desc: Para ordenar por fecha
player_recent: Para búsquedas por jugador
```

### Beneficios:
- Consultas más rápidas (O(log n) vs O(n))
- Menor uso de CPU
- Mejor experiencia de usuario

---

## 7. Manejo de Errores Seguro ⚠️

### Producción vs Desarrollo:
```python
# Desarrollo: Muestra detalles del error
if not settings.is_production:
    return {"error": "...", "detail": str(exc)}

# Producción: Oculta detalles sensibles
if settings.is_production:
    return {"error": "Error interno del servidor"}
```

### Logging:
- Errores registrados en consola (en producción usar logging profesional)
- No exponer stack traces al cliente
- No revelar estructura de base de datos

---

## 8. Protección contra Ataques Comunes 🛡️

### Inyección NoSQL:
✅ Uso de Motor (driver oficial)
✅ Validación estricta con Pydantic
✅ No concatenación de strings en queries

### XSS (Cross-Site Scripting):
✅ Sanitización de nombres
✅ Solo caracteres alfanuméricos
✅ Headers de seguridad

### CSRF (Cross-Site Request Forgery):
✅ CORS estricto
✅ Validación de origen

### DDoS (Distributed Denial of Service):
✅ Rate limiting agresivo
✅ Límites por IP
✅ Timeouts de conexión MongoDB

### Host Header Injection:
✅ TrustedHostMiddleware en producción
✅ Validación de hosts permitidos

---

## 9. Checklist Pre-Deployment ✅

Antes de hacer deploy a producción:

- [ ] Cambiar `ENVIRONMENT=production` en `.env`
- [ ] Configurar `BACKEND_CORS_ORIGINS` con dominio real
- [ ] Verificar que `.env` NO esté en Git
- [ ] MongoDB: Habilitar IP Whitelist
- [ ] MongoDB: Configurar usuario con privilegios mínimos
- [ ] Habilitar HTTPS (Let's Encrypt)
- [ ] Configurar TrustedHostMiddleware con tu dominio
- [ ] Desactivar `/docs` y `/redoc` (automático en producción)
- [ ] Configurar logging profesional (ej: Sentry)
- [ ] Configurar backup de MongoDB
- [ ] Revisar límites de rate limiting según tráfico esperado
- [ ] Configurar monitoreo (uptime, errores)

---

## 10. Mantenimiento Continuo 🔄

### Actualizaciones:
- Actualizar dependencias regularmente
- Revisar CVEs de seguridad
- Monitorear logs de errores
- Analizar patrones de ataques

### Auditorías:
- Revisar logs de rate limiting
- Analizar intentos de entrada inválida
- Verificar integridad de datos
- Revisar accesos a MongoDB

---

## 📚 Referencias OWASP

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

---

## 🚨 Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, por favor repórtala de manera responsable:
- NO crear issues públicos
- Contactar directamente al equipo de desarrollo
- Proporcionar detalles técnicos y pasos para reproducir

---

**Última actualización**: Enero 2025
**Versión de seguridad**: 1.0.0