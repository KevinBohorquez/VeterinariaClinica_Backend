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
from app.api.v1.endpoints.mascota import router as mascotas_router
from app.api.v1.endpoints.usuarios import router as usuarios_router
from app.api.v1.endpoints.administradores import router as administradores_router
from app.api.v1.endpoints.catalogos import router as catalogos_router
from app.api.v1.endpoints.consultas import router as consultas_router

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
app.include_router(mascotas_router, prefix="/api/v1/mascotas", tags=["mascotas"])
app.include_router(usuarios_router, prefix="/api/v1/usuarios", tags=["usuarios"])
app.include_router(administradores_router, prefix="/api/v1/administradores", tags=["administradores"])
app.include_router(catalogos_router, prefix="/api/v1/catalogos", tags=["catalogos"])
app.include_router(consultas_router, prefix="/api/v1/consultas", tags=["consultas"])


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
                "recepcionistas": "/api/v1/recepcionistas - Gestión de recepcionistas",
                "mascotas": "/api/v1/mascotas - Gestión de mascotas",
                "usuarios": "/api/v1/usuarios - Gestión de usuarios del sistema",
                "administradores": "/api/v1/administradores - Gestión de administradores",
                "catalogos": "/api/v1/catalogos - Gestión de catálogos (razas, servicios, patologías)",
                "consultas": "/api/v1/consultas - Gestión de consultas y procesos clínicos"
            }
        },
        "examples": {
            "clientes": {
                "list": "GET /api/v1/clientes",
                "create": "POST /api/v1/clientes",
                "get_by_id": "GET /api/v1/clientes/{id}",
                "get_by_dni": "GET /api/v1/clientes/dni/{dni}",
                "get_by_email": "GET /api/v1/clientes/email/{email}",
                "search": "POST /api/v1/clientes/search",
                "update": "PUT /api/v1/clientes/{id}",
                "delete": "DELETE /api/v1/clientes/{id}",
                "mascotas": "GET /api/v1/clientes/{id}/mascotas"
            },
            "veterinarios": {
                "list": "GET /api/v1/veterinarios",
                "create": "POST /api/v1/veterinarios",
                "get_by_id": "GET /api/v1/veterinarios/{id}",
                "get_by_dni": "GET /api/v1/veterinarios/dni/{dni}",
                "get_by_email": "GET /api/v1/veterinarios/email/{email}",
                "get_by_codigo_cmvp": "GET /api/v1/veterinarios/codigo-cmvp/{codigo}",
                "disponibles": "GET /api/v1/veterinarios/disponibles",
                "por_especialidad": "GET /api/v1/veterinarios/especialidad/{id}",
                "update": "PUT /api/v1/veterinarios/{id}",
                "search": "POST /api/v1/veterinarios/search"
            },
            "recepcionistas": {
                "list": "GET /api/v1/recepcionistas",
                "create": "POST /api/v1/recepcionistas",
                "get_by_id": "GET /api/v1/recepcionistas/{id}",
                "get_by_dni": "GET /api/v1/recepcionistas/dni/{dni}",
                "get_by_email": "GET /api/v1/recepcionistas/email/{email}",
                "por_turno": "GET /api/v1/recepcionistas/turno/{turno}",
                "update": "PUT /api/v1/recepcionistas/{id}",
                "search": "POST /api/v1/recepcionistas/search"
            },
            "mascotas": {
                "list": "GET /api/v1/mascotas",
                "create": "POST /api/v1/mascotas?cliente_id={id}",
                "get_by_id": "GET /api/v1/mascotas/{id}",
                "get_with_details": "GET /api/v1/mascotas/{id}/details",
                "update": "PUT /api/v1/mascotas/{id}",
                "delete": "DELETE /api/v1/mascotas/{id}",
                "search": "POST /api/v1/mascotas/search",
                "por_cliente": "GET /api/v1/mascotas/cliente/{cliente_id}/list",
                "stats_sexo": "GET /api/v1/mascotas/stats/por-sexo",
                "no_esterilizadas": "GET /api/v1/mascotas/no-esterilizadas/list"
            },
            "usuarios": {
                "list": "GET /api/v1/usuarios",
                "create": "POST /api/v1/usuarios",
                "get_by_id": "GET /api/v1/usuarios/{id}",
                "get_by_username": "GET /api/v1/usuarios/username/{username}",
                "login": "POST /api/v1/usuarios/login",
                "change_password": "POST /api/v1/usuarios/{id}/change-password",
                "activate": "POST /api/v1/usuarios/{id}/activate",
                "deactivate": "POST /api/v1/usuarios/{id}/deactivate",
                "search": "POST /api/v1/usuarios/search",
                "stats": "GET /api/v1/usuarios/stats"
            },
            "administradores": {
                "list": "GET /api/v1/administradores",
                "create": "POST /api/v1/administradores",
                "get_by_id": "GET /api/v1/administradores/{id}",
                "get_by_dni": "GET /api/v1/administradores/dni/{dni}",
                "get_by_email": "GET /api/v1/administradores/email/{email}",
                "update": "PUT /api/v1/administradores/{id}",
                "search": "POST /api/v1/administradores/search",
                "stats": "GET /api/v1/administradores/stats",
                "with_usuario": "GET /api/v1/administradores/{id}/with-usuario"
            },
            "catalogos": {
                "razas": {
                    "list": "GET /api/v1/catalogos/razas",
                    "create": "POST /api/v1/catalogos/razas",
                    "get_by_id": "GET /api/v1/catalogos/razas/{id}",
                    "search": "GET /api/v1/catalogos/razas/search?nombre={nombre}"
                },
                "especialidades": {
                    "list": "GET /api/v1/catalogos/especialidades",
                    "create": "POST /api/v1/catalogos/especialidades",
                    "get_by_id": "GET /api/v1/catalogos/especialidades/{id}",
                    "search": "GET /api/v1/catalogos/especialidades/search?descripcion={desc}"
                },
                "servicios": {
                    "list": "GET /api/v1/catalogos/servicios",
                    "create": "POST /api/v1/catalogos/servicios",
                    "get_by_id": "GET /api/v1/catalogos/servicios/{id}",
                    "update": "PUT /api/v1/catalogos/servicios/{id}",
                    "activos": "GET /api/v1/catalogos/servicios/activos",
                    "por_tipo": "GET /api/v1/catalogos/servicios/tipo/{tipo_id}",
                    "por_precio": "GET /api/v1/catalogos/servicios/precio?min={min}&max={max}"
                },
                "patologias": {
                    "list": "GET /api/v1/catalogos/patologias",
                    "create": "POST /api/v1/catalogos/patologias",
                    "get_by_id": "GET /api/v1/catalogos/patologias/{id}",
                    "por_especie": "GET /api/v1/catalogos/patologias/especie/{especie}",
                    "por_gravedad": "GET /api/v1/catalogos/patologias/gravedad/{gravedad}",
                    "cronicas": "GET /api/v1/catalogos/patologias/cronicas",
                    "contagiosas": "GET /api/v1/catalogos/patologias/contagiosas"
                }
            },
            "consultas": {
                "solicitudes": {
                    "list": "GET /api/v1/consultas/solicitudes",
                    "create": "POST /api/v1/consultas/solicitudes",
                    "get_by_id": "GET /api/v1/consultas/solicitudes/{id}",
                    "update": "PUT /api/v1/consultas/solicitudes/{id}",
                    "search": "POST /api/v1/consultas/solicitudes/search",
                    "cambiar_estado": "PATCH /api/v1/consultas/solicitudes/{id}/estado",
                    "por_mascota": "GET /api/v1/consultas/solicitudes/mascota/{id}",
                    "pendientes": "GET /api/v1/consultas/solicitudes/pendientes"
                },
                "triajes": {
                    "list": "GET /api/v1/consultas/triajes",
                    "create": "POST /api/v1/consultas/triajes",
                    "get_by_id": "GET /api/v1/consultas/triajes/{id}",
                    "update": "PUT /api/v1/consultas/triajes/{id}",
                    "search": "POST /api/v1/consultas/triajes/search",
                    "por_urgencia": "GET /api/v1/consultas/triajes/urgencia/{clasificacion}",
                    "criticos": "GET /api/v1/consultas/triajes/criticos/recientes",
                    "stats_urgencia": "GET /api/v1/consultas/triajes/estadisticas/urgencia",
                    "signos_vitales": "GET /api/v1/consultas/triajes/estadisticas/signos-vitales"
                },
                "consultas_medicas": {
                    "list": "GET /api/v1/consultas/consultas",
                    "create": "POST /api/v1/consultas/consultas",
                    "get_by_id": "GET /api/v1/consultas/consultas/{id}",
                    "search": "POST /api/v1/consultas/consultas/search",
                    "por_veterinario": "GET /api/v1/consultas/consultas/veterinario/{id}",
                    "seguimientos": "GET /api/v1/consultas/consultas/seguimientos"
                },
                "diagnosticos": {
                    "list": "GET /api/v1/consultas/diagnosticos",
                    "create": "POST /api/v1/consultas/diagnosticos",
                    "por_consulta": "GET /api/v1/consultas/diagnosticos/consulta/{id}",
                    "confirmados": "GET /api/v1/consultas/diagnosticos/confirmados"
                },
                "tratamientos": {
                    "list": "GET /api/v1/consultas/tratamientos",
                    "create": "POST /api/v1/consultas/tratamientos",
                    "por_consulta": "GET /api/v1/consultas/tratamientos/consulta/{id}",
                    "activos": "GET /api/v1/consultas/tratamientos/activos"
                },
                "citas": {
                    "list": "GET /api/v1/consultas/citas",
                    "create": "POST /api/v1/consultas/citas",
                    "get_by_id": "GET /api/v1/consultas/citas/{id}",
                    "update": "PUT /api/v1/consultas/citas/{id}",
                    "search": "POST /api/v1/consultas/citas/search",
                    "programadas": "GET /api/v1/consultas/citas/programadas",
                    "hoy": "GET /api/v1/consultas/citas/hoy",
                    "cancelar": "POST /api/v1/consultas/citas/{id}/cancelar"
                },
                "historial": {
                    "por_mascota": "GET /api/v1/consultas/historial/mascota/{id}",
                    "add_evento": "POST /api/v1/consultas/historial/eventos",
                    "search": "POST /api/v1/consultas/historial/search",
                    "resumen": "GET /api/v1/consultas/historial/mascota/{id}/resumen"
                }
            }
        },
        "modulos_completos": {
            "gestion_usuarios": [
                "clientes", "veterinarios", "recepcionistas",
                "usuarios", "administradores"
            ],
            "catalogos_sistema": [
                "razas", "especialidades", "servicios",
                "patologias", "tipos_servicios"
            ],
            "procesos_clinicos": [
                "solicitudes", "triajes", "consultas",
                "diagnosticos", "tratamientos", "historial"
            ],
            "gestion_citas": [
                "programacion_citas", "servicios_solicitados",
                "resultados_servicios"
            ]
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
        "total_endpoints": 80,
        "modules": {
            "clientes": {
                "description": "Gestión de clientes propietarios",
                "endpoints": 9,
                "features": ["CRUD completo", "Búsqueda avanzada", "Filtros", "Paginación", "Relación con mascotas"]
            },
            "veterinarios": {
                "description": "Gestión de veterinarios",
                "endpoints": 12,
                "features": ["CRUD completo", "Especialidades", "Disponibilidad", "Turnos", "Código CMVP"]
            },
            "recepcionistas": {
                "description": "Gestión de recepcionistas",
                "endpoints": 10,
                "features": ["CRUD completo", "Turnos", "Estados", "Búsqueda", "Gestión por turno"]
            },
            "mascotas": {
                "description": "Gestión de mascotas",
                "endpoints": 9,
                "features": ["CRUD completo", "Relación cliente-mascota", "Estadísticas", "Filtros por raza/sexo"]
            },
            "usuarios": {
                "description": "Gestión de usuarios del sistema",
                "endpoints": 10,
                "features": ["Autenticación", "Roles", "Cambio contraseñas", "Estados", "Estadísticas"]
            },
            "administradores": {
                "description": "Gestión de administradores",
                "endpoints": 8,
                "features": ["CRUD completo", "Búsqueda", "Estadísticas", "Relación con usuarios"]
            },
            "catalogos": {
                "description": "Gestión de catálogos del sistema",
                "endpoints": 22,
                "features": ["Razas", "Especialidades", "Servicios", "Patologías", "Tipos de servicios"]
            },
            "consultas": {
                "description": "Procesos clínicos completos",
                "endpoints": 30,
                "features": ["Solicitudes", "Triajes", "Consultas", "Diagnósticos", "Tratamientos", "Citas", "Historial"]
            }
        },
        "database": {
            "engine": "MySQL",
            "orm": "SQLAlchemy",
            "migrations": "Alembic",
            "connection_pool": "Habilitado"
        },
        "security": {
            "authentication": "JWT (próximamente)",
            "authorization": "Role-based",
            "cors": "Habilitado",
            "rate_limiting": "Pendiente"
        },
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "deployment": {
            "platform": "Railway",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "health_check": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)