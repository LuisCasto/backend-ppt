from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime
from pymongo import DESCENDING, IndexModel

class Database:
    client: AsyncIOMotorClient = None
    
db = Database()

async def get_database():
    return db.client[settings.DATABASE_NAME]

async def connect_to_mongo():
    """Conectar a MongoDB al iniciar la aplicación"""
    print("🔌 Conectando a MongoDB...")
    
    try:
        # Configuración de conexión segura
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=10,  # Limitar conexiones simultáneas
            minPoolSize=1,
            maxIdleTimeMS=45000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        
        # Verificar conexión
        await db.client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB Atlas!")
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Cerrar conexión al apagar la aplicación"""
    print("🔌 Cerrando conexión a MongoDB...")
    if db.client:
        db.client.close()
        print("✅ Conexión cerrada")

async def create_indexes():
    """Crear índices para optimizar consultas y garantizar unicidad"""
    print("📊 Creando índices en MongoDB...")
    
    try:
        database = await get_database()
        
        # Índices para leaderboard_normal
        leaderboard_normal = database["leaderboard_normal"]
        await leaderboard_normal.create_indexes([
            IndexModel([("score", DESCENDING)], name="score_desc"),
            IndexModel([("timestamp", DESCENDING)], name="timestamp_desc"),
            IndexModel([("player_name", 1), ("timestamp", DESCENDING)], name="player_recent")
        ])
        
        # Índices para leaderboard_imposible
        leaderboard_imposible = database["leaderboard_imposible"]
        await leaderboard_imposible.create_indexes([
            IndexModel([("score", DESCENDING)], name="score_desc"),
            IndexModel([("timestamp", DESCENDING)], name="timestamp_desc"),
            IndexModel([("player_name", 1), ("timestamp", DESCENDING)], name="player_recent")
        ])
        
        print("✅ Índices creados exitosamente")
        
    except Exception as e:
        print(f"⚠️ Error creando índices: {e}")

async def save_leaderboard_entry(player_name: str, score: int, mode: str):
    """
    Guardar entrada en el leaderboard con validaciones
    """
    # Validaciones de seguridad
    if not player_name or len(player_name) > settings.MAX_PLAYER_NAME_LENGTH:
        raise ValueError("Nombre de jugador inválido")
    
    if score < -500 or score > 500:
        raise ValueError("Puntuación fuera de rango válido")
    
    if mode not in settings.ALLOWED_GAME_MODES:
        raise ValueError("Modo de juego inválido")
    
    database = await get_database()
    collection_name = f"leaderboard_{mode}"
    collection = database[collection_name]
    
    # Documento con timestamp UTC
    entry = {
        "player_name": player_name.upper().strip(),
        "score": int(score),
        "timestamp": datetime.utcnow()
    }
    
    try:
        result = await collection.insert_one(entry)
        return result.inserted_id
    except Exception as e:
        print(f"Error guardando entrada: {e}")
        raise

async def get_leaderboard(mode: str, limit: int = 10):
    """
    Obtener top jugadores del leaderboard con límite
    """
    # Validación de modo
    if mode not in settings.ALLOWED_GAME_MODES:
        raise ValueError("Modo de juego inválido")
    
    # Validar y limitar el límite
    if limit < 1 or limit > 100:
        limit = 10
    
    database = await get_database()
    collection_name = f"leaderboard_{mode}"
    collection = database[collection_name]
    
    try:
        # Usar índice para ordenar por score descendente
        cursor = collection.find(
            {},
            {"_id": 0, "player_name": 1, "score": 1, "timestamp": 1}
        ).sort("score", DESCENDING).limit(limit)
        
        entries = await cursor.to_list(length=limit)
        return entries
        
    except Exception as e:
        print(f"Error obteniendo leaderboard: {e}")
        raise