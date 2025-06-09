# main.py - Sistema Veterinaria API
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import os
from datetime import datetime

from app.config.database import get_db
from app.models.clientes import Cliente

# ✅ IMPORTAR LOS ROUTERS CORREGIDOS DE LA CARPETA ENDPOINTS
from app.api.v1.endpoints.clientes import router as clientes_router
from app.api.v1.endpoints.veterinarios import router as veterinarios_router
from app.api.v1.endpoints.recepcionistas import router as recepcionistas_router
from app.api.v1.endpoints.mascota import router as mascotas_router  # ← Comentado hasta crear

app = FastAPI(
    title="🏥 Sistema Veterinaria API",
    description="API para gestión integral de veterinaria",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ INCLUIR LOS ROUTERS CON SUS PREFIJOS
app.include_router(clientes_router, prefix="/api/v1/clientes", tags=["clientes"])
app.include_router(veterinarios_router, prefix="/api/v1/veterinarios", tags=["veterinarios"])
app.include_router(recepcionistas_router, prefix="/api/v1/recepcionistas", tags=["recepcionistas"])

app.include_router(mascotas_router, prefix="/api/v1/mascotas", tags=["mascotas"])  # ← Comentado hasta crear

# ===== ENDPOINTS BÁSICOS (solo estos en main) =====

@app.get("/")
async def root():
    return {
        "message": "🏥 Sistema Veterinaria API funcionando!",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "status": "OK",
        "endpoints": {
            "health": "/health - Estado del sistema",
            "test_db": "/test-db - Probar conexión DB",
            "stats": "/stats - Estadísticas generales",
            "docs": "/docs - Documentación Swagger",
            "redoc": "/redoc - Documentación ReDoc",
            "api_v1": {
                "clientes": "/api/v1/clientes - Gestión de clientes",
                "veterinarios": "/api/v1/veterinarios - Gestión de veterinarios",
                "recepcionistas": "/api/v1/recepcionistas - Gestión de recepcionistas"
            }
        },
        "examples": {
            "clientes": {
                "list": "GET /api/v1/clientes",
                "create": "POST /api/v1/clientes",
                "get_by_id": "GET /api/v1/clientes/{id}",
                "get_by_dni": "GET /api/v1/clientes/dni/{dni}",
                "search": "POST /api/v1/clientes/search"
            },
            "veterinarios": {
                "list": "GET /api/v1/veterinarios",
                "create": "POST /api/v1/veterinarios",
                "get_by_id": "GET /api/v1/veterinarios/{id}",
                "get_by_dni": "GET /api/v1/veterinarios/dni/{dni}",
                "disponibles": "GET /api/v1/veterinarios/disponibles"
            },
            "recepcionistas": {
                "list": "GET /api/v1/recepcionistas",
                "create": "POST /api/v1/recepcionistas",
                "get_by_id": "GET /api/v1/recepcionistas/{id}",
                "activas": "GET /api/v1/recepcionistas/activas",
                "por_turno": "GET /api/v1/recepcionistas/turno/{turno}"
            }
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "veterinaria-api",
        "version": "1.0.0"
    }

@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Probar conexión a la base de datos"""
    try:
        # Test simple
        result = db.execute("SELECT 1 as test").fetchone()

        # Test con tablas principales
        cliente_count = db.query(Cliente).count()

        return {
            "status": "success",
            "message": "Conexión exitosa a la base de datos",
            "test_query": "OK",
            "total_clientes": cliente_count,
            "timestamp": datetime.now().isoformat()
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )

@app.get("/stats")
async def get_estadisticas_generales(db: Session = Depends(get_db)):
    """Obtener estadísticas generales del sistema"""
    try:
        from app.models.veterinario import Veterinario
        from app.models.recepcionista import Recepcionista

        # Estadísticas de clientes
        total_clientes = db.query(Cliente).count()
        clientes_activos = db.query(Cliente).filter(Cliente.estado == "Activo").count()

        # Estadísticas de veterinarios
        total_veterinarios = db.query(Veterinario).count()
        veterinarios_disponibles = db.query(Veterinario).filter(Veterinario.disposicion == "Libre").count()

        # Estadísticas de recepcionistas
        total_recepcionistas = db.query(Recepcionista).count()
        recepcionistas_activas = db.query(Recepcionista).filter(Recepcionista.estado == "Activo").count()

        return {
            "resumen": {
                "total_usuarios": total_clientes + total_veterinarios + total_recepcionistas,
                "timestamp": datetime.now().isoformat()
            },
            "clientes": {
                "total": total_clientes,
                "activos": clientes_activos,
                "inactivos": total_clientes - clientes_activos,
                "porcentaje_activos": round((clientes_activos / total_clientes * 100), 2) if total_clientes > 0 else 0
            },
            "veterinarios": {
                "total": total_veterinarios,
                "disponibles": veterinarios_disponibles,
                "ocupados": total_veterinarios - veterinarios_disponibles,
                "porcentaje_disponibles": round((veterinarios_disponibles / total_veterinarios * 100), 2) if total_veterinarios > 0 else 0
            },
            "recepcionistas": {
                "total": total_recepcionistas,
                "activas": recepcionistas_activas,
                "inactivas": total_recepcionistas - recepcionistas_activas,
                "porcentaje_activas": round((recepcionistas_activas / total_recepcionistas * 100), 2) if total_recepcionistas > 0 else 0
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

@app.get("/info")
async def get_api_info():
    """Información detallada de la API"""
    return {
        "name": "Sistema Veterinaria API",
        "version": "1.0.0",
        "description": "API completa para gestión de veterinaria",
        "modules": {
            "clientes": {
                "description": "Gestión de clientes",
                "endpoints": 8,
                "features": ["CRUD completo", "Búsqueda", "Filtros", "Paginación"]
            },
            "veterinarios": {
                "description": "Gestión de veterinarios",
                "endpoints": 10,
                "features": ["CRUD completo", "Especialidades", "Disponibilidad", "Citas"]
            },
            "recepcionistas": {
                "description": "Gestión de recepcionistas",
                "endpoints": 9,
                "features": ["CRUD completo", "Turnos", "Estados", "Búsqueda"]
            }
        },
        "database": {
            "engine": "MySQL",
            "orm": "SQLAlchemy",
            "migrations": "Alembic"
        },
        "authentication": "JWT (próximamente)",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)