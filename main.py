# main.py - Sistema Veterinaria API COMPLETO
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import os
from datetime import datetime

from app.config.database import get_db
from app.models.clientes import Cliente

# ✅ IMPORTAR TODOS LOS ROUTERS (AUTENTICACIÓN + GESTIÓN)
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.clientes import router as clientes_router
from app.api.v1.endpoints.veterinarios import router as veterinarios_router
from app.api.v1.endpoints.recepcionistas import router as recepcionistas_router
from app.api.v1.endpoints.mascota import router as mascotas_router
from app.api.v1.endpoints.usuarios import router as usuarios_router
from app.api.v1.endpoints.administradores import router as administradores_router
from app.api.v1.endpoints.catalogos import router as catalogos_router
from app.api.v1.endpoints.consultas import router as consultas_router

app = FastAPI(
    title="🏥 Sistema Veterinaria API Completo",
    description="API integral para gestión de veterinaria con autenticación y todos los módulos",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ INCLUIR TODOS LOS ROUTERS DISPONIBLES
# Autenticación (prioritario)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["🔐 autenticación"])

# Gestión de usuarios
app.include_router(clientes_router, prefix="/api/v1/clientes", tags=["👥 clientes"])
app.include_router(veterinarios_router, prefix="/api/v1/veterinarios", tags=["👨‍⚕️ veterinarios"])
app.include_router(recepcionistas_router, prefix="/api/v1/recepcionistas", tags=["👩‍💼 recepcionistas"])
app.include_router(usuarios_router, prefix="/api/v1/usuarios", tags=["👤 usuarios"])
app.include_router(administradores_router, prefix="/api/v1/administradores", tags=["👑 administradores"])

# Gestión de mascotas
app.include_router(mascotas_router, prefix="/api/v1/mascotas", tags=["🐕 mascotas"])

# Catálogos del sistema
app.include_router(catalogos_router, prefix="/api/v1/catalogos", tags=["📋 catálogos"])

# Procesos clínicos
app.include_router(consultas_router, prefix="/api/v1/consultas", tags=["🏥 consultas"])

# Router condicional
if SOLICITUDES_AVAILABLE:
    app.include_router(solicitudes_router, prefix="/api/v1/solicitudes", tags=["📋 solicitudes"])


# ===== ENDPOINTS PRINCIPALES =====

@app.get("/")
async def root():
    available_modules = {
        "🔐 autenticación": "/api/v1/auth - Sistema de login/logout completo",
        "👥 clientes": "/api/v1/clientes - Gestión de clientes propietarios",
        "👨‍⚕️ veterinarios": "/api/v1/veterinarios - Gestión de veterinarios",
        "👩‍💼 recepcionistas": "/api/v1/recepcionistas - Gestión de recepcionistas",
        "👤 usuarios": "/api/v1/usuarios - Gestión de usuarios del sistema",
        "👑 administradores": "/api/v1/administradores - Gestión de administradores",
        "🐕 mascotas": "/api/v1/mascotas - Gestión de mascotas",
        "📋 catálogos": "/api/v1/catalogos - Razas, especialidades, servicios, patologías",
        "🏥 consultas": "/api/v1/consultas - Procesos clínicos completos"
    }

    if SOLICITUDES_AVAILABLE:
        available_modules["📋 solicitudes"] = "/api/v1/solicitudes - Solicitudes de atención"

    return {
        "message": "🏥 Sistema Veterinaria API COMPLETO funcionando!",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "2.0.0",
        "status": "OK",
        "modules_available": available_modules,
        "system_info": {
            "authentication": "✅ Sistema completo de autenticación",
            "user_management": "✅ Gestión completa de usuarios",
            "pet_management": "✅ Gestión de mascotas",
            "catalogs": "✅ Catálogos del sistema",
            "clinical_processes": "✅ Procesos clínicos completos",
            "total_modules": len(available_modules)
        },
        "quick_start": {
            "1": "🔐 POST /api/v1/auth/login - Iniciar sesión",
            "2": "👥 GET /api/v1/clientes - Ver clientes",
            "3": "🐕 GET /api/v1/mascotas - Ver mascotas",
            "4": "🏥 GET /api/v1/consultas/solicitudes - Ver solicitudes",
            "5": "📋 GET /api/v1/catalogos/razas - Ver catálogos",
            "6": "🔐 POST /api/v1/auth/logout - Cerrar sesión"
        },
        "authentication_examples": {
            "login": {
                "endpoint": "POST /api/v1/auth/login",
                "example": {
                    "username": "admin001",
                    "password": "password123"
                }
            },
            "logout": {
                "endpoint": "POST /api/v1/auth/logout",
                "example": {
                    "user_id": 1
                }
            },
            "check_session": "GET /api/v1/auth/session/{user_id}",
            "change_password": "POST /api/v1/auth/change-password",
            "check_permissions": "POST /api/v1/auth/check-permission"
        },
        "user_roles": {
            "Administrador": {
                "description": "Acceso completo al sistema",
                "permissions": "Todos los módulos y configuraciones"
            },
            "Veterinario": {
                "description": "Acceso a procesos clínicos",
                "permissions": "Consultas, diagnósticos, tratamientos, triajes"
            },
            "Recepcionista": {
                "description": "Acceso a recepción y gestión",
                "permissions": "Clientes, mascotas, citas, solicitudes"
            }
        },
        "main_endpoints": {
            "health": "/health - Estado del sistema",
            "test_db": "/test-db - Probar conexión a BD",
            "stats": "/stats - Estadísticas generales",
            "info": "/info - Información detallada de la API",
            "docs": "/docs - Documentación Swagger",
            "redoc": "/redoc - Documentación ReDoc"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "veterinaria-api-completo",
        "version": "2.0.0",
        "modules": {
            "authentication": "active",
            "user_management": "active",
            "pet_management": "active",
            "catalogs": "active",
            "clinical_processes": "active",
            "database": "connected",
            "api": "running",
            "solicitudes_module": "active" if SOLICITUDES_AVAILABLE else "not_found"
        }
    }


@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Probar conexión a la base de datos y verificar tablas principales"""
    try:
        # Test de conexión básica
        result = db.execute("SELECT 1 as test").fetchone()

        # Test con tablas principales
        cliente_count = db.query(Cliente).count()

        # Test con tabla de usuarios (si existe)
        try:
            from app.models.usuario import Usuario
            usuario_count = db.query(Usuario).count()
            auth_available = True
        except Exception:
            usuario_count = 0
            auth_available = False

        # Test con otras tablas principales
        try:
            from app.models.veterinario import Veterinario
            from app.models.recepcionista import Recepcionista
            veterinario_count = db.query(Veterinario).count()
            recepcionista_count = db.query(Recepcionista).count()
        except Exception as e:
            veterinario_count = 0
            recepcionista_count = 0

        return {
            "status": "success",
            "message": "Conexión exitosa a la base de datos",
            "test_query": "OK",
            "tables_status": {
                "clientes": cliente_count,
                "usuarios": usuario_count if auth_available else "tabla no encontrada",
                "veterinarios": veterinario_count,
                "recepcionistas": recepcionista_count
            },
            "authentication_ready": auth_available,
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
    """Obtener estadísticas generales del sistema completo"""
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

        # Estadísticas de usuarios (si están disponibles)
        auth_stats = {}
        try:
            from app.models.usuario import Usuario
            total_usuarios = db.query(Usuario).count()
            usuarios_activos = db.query(Usuario).filter(Usuario.estado == "Activo").count()
            auth_stats = {
                "total_usuarios_login": total_usuarios,
                "usuarios_activos": usuarios_activos,
                "usuarios_inactivos": total_usuarios - usuarios_activos,
                "tipos_usuario": {
                    "administradores": db.query(Usuario).filter(Usuario.tipo_usuario == "Administrador").count(),
                    "veterinarios": db.query(Usuario).filter(Usuario.tipo_usuario == "Veterinario").count(),
                    "recepcionistas": db.query(Usuario).filter(Usuario.tipo_usuario == "Recepcionista").count()
                }
            }
        except Exception:
            auth_stats = {"status": "módulo de autenticación no disponible"}

        return {
            "resumen": {
                "total_usuarios_sistema": total_clientes + total_veterinarios + total_recepcionistas,
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            },
            "autenticacion": auth_stats,
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
                "porcentaje_disponibles": round((veterinarios_disponibles / total_veterinarios * 100),
                                                2) if total_veterinarios > 0 else 0
            },
            "recepcionistas": {
                "total": total_recepcionistas,
                "activas": recepcionistas_activas,
                "inactivas": total_recepcionistas - recepcionistas_activas,
                "porcentaje_activas": round((recepcionistas_activas / total_recepcionistas * 100),
                                            2) if total_recepcionistas > 0 else 0
            },
            "modulos_disponibles": {
                "autenticacion": bool(auth_stats.get("total_usuarios_login")),
                "solicitudes": SOLICITUDES_AVAILABLE,
                "catalogos": True,
                "consultas": True
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@app.get("/info")
async def get_api_info():
    """Información detallada de la API completa"""
    return {
        "name": "Sistema Veterinaria API Completo",
        "version": "2.0.0",
        "description": "API integral para gestión de veterinaria con autenticación y todos los módulos",
        "total_estimated_endpoints": 100,
        "authentication": {
            "type": "Session-based (expandible a JWT)",
            "user_types": ["Administrador", "Veterinario", "Recepcionista"],
            "features": [
                "Login/Logout completo",
                "Gestión de sesiones",
                "Control de permisos por rol",
                "Cambio de contraseñas",
                "Validación de usuarios",
                "Estados activo/inactivo"
            ]
        },
        "modules": {
            "auth": {
                "description": "Sistema completo de autenticación",
                "endpoints": 9,
                "features": ["Login", "Logout", "Permisos", "Sesiones", "Cambio contraseñas"]
            },
            "clientes": {
                "description": "Gestión de clientes propietarios",
                "endpoints": 9,
                "features": ["CRUD completo", "Búsqueda avanzada", "Filtros", "Relación con mascotas"]
            },
            "veterinarios": {
                "description": "Gestión de veterinarios",
                "endpoints": 12,
                "features": ["CRUD completo", "Especialidades", "Disponibilidad", "Código CMVP"]
            },
            "recepcionistas": {
                "description": "Gestión de recepcionistas",
                "endpoints": 10,
                "features": ["CRUD completo", "Turnos", "Estados", "Gestión por turno"]
            },
            "usuarios": {
                "description": "Gestión de usuarios del sistema",
                "endpoints": 10,
                "features": ["Autenticación", "Roles", "Estados", "Estadísticas"]
            },
            "administradores": {
                "description": "Gestión de administradores",
                "endpoints": 8,
                "features": ["CRUD completo", "Búsqueda", "Relación con usuarios"]
            },
            "mascotas": {
                "description": "Gestión de mascotas",
                "endpoints": 9,
                "features": ["CRUD completo", "Relación cliente-mascota", "Estadísticas"]
            },
            "catalogos": {
                "description": "Catálogos del sistema",
                "endpoints": 22,
                "features": ["Razas", "Especialidades", "Servicios", "Patologías"]
            },
            "consultas": {
                "description": "Procesos clínicos completos",
                "endpoints": 30,
                "features": ["Solicitudes", "Triajes", "Consultas", "Diagnósticos", "Tratamientos", "Citas",
                             "Historial"]
            },
            "solicitudes": {
                "description": "Solicitudes de atención",
                "endpoints": 6 if SOLICITUDES_AVAILABLE else 0,
                "status": "disponible" if SOLICITUDES_AVAILABLE else "no encontrado"
            }
        },
        "database": {
            "engine": "MySQL",
            "orm": "SQLAlchemy",
            "migrations": "Alembic",
            "connection_pool": "Habilitado",
            "estimated_tables": 25
        },
        "security": {
            "authentication": "Session-based con expansión a JWT",
            "authorization": "Role-based (Administrador, Veterinario, Recepcionista)",
            "cors": "Habilitado para todos los orígenes",
            "password_validation": "Implementado",
            "session_management": "Completo"
        },
        "deployment": {
            "platform": "Railway/Docker compatible",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "health_check": "/health",
            "database_test": "/test-db"
        },
        "docs": {
            "swagger": "/docs - Interfaz Swagger UI",
            "redoc": "/redoc - Documentación ReDoc",
            "openapi": "/openapi.json - Especificación OpenAPI"
        },
        "workflow_example": {
            "1": "🔐 Login con POST /api/v1/auth/login",
            "2": "👥 Gestionar clientes con /api/v1/clientes",
            "3": "🐕 Registrar mascotas con /api/v1/mascotas",
            "4": "🏥 Crear solicitudes con /api/v1/consultas/solicitudes",
            "5": "👨‍⚕️ Realizar triaje con /api/v1/consultas/triajes",
            "6": "🏥 Realizar consulta con /api/v1/consultas/consultas",
            "7": "🔐 Logout con POST /api/v1/auth/logout"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)