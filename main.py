# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  # <--- IMPORTANTE: Necesario para devolver errores
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime

from app.config.database import get_db
# ... (Tus otros imports siguen igual) ...
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.clientes import router as clientes_router
from app.api.v1.endpoints.veterinarios import router as veterinarios_router
from app.api.v1.endpoints.recepcionistas import router as recepcionistas_router
from app.api.v1.endpoints.mascota import router as mascotas_router
from app.api.v1.endpoints.usuarios import router as usuarios_router
from app.api.v1.endpoints.administradores import router as administradores_router
from app.api.v1.endpoints.catalogos import router as catalogos_router
from app.api.v1.endpoints.consultas import router as consultas_router
from app.api.v1.endpoints.solicitudes import router as solicitudes_router
from app.api.v1.endpoints.triaje import router as triaje_router
from app.api.v1.endpoints.servicio_solicitado import router as servicio_solicitado_router

app = FastAPI(
    title="🏥 Sistema Veterinaria API Completo",
    description="API integral para gestión de veterinaria",
    version="2.0.0"
)

# Configuración CORS (Asegúrate de incluir tu frontend aquí)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cambiar por dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["🔐 autenticación"])
app.include_router(clientes_router, prefix="/api/v1/clientes", tags=["👥 clientes"])
app.include_router(veterinarios_router, prefix="/api/v1/veterinarios", tags=["👨‍⚕️ veterinarios"])
app.include_router(recepcionistas_router, prefix="/api/v1/recepcionistas", tags=["👩‍💼 recepcionistas"])
app.include_router(usuarios_router, prefix="/api/v1/usuarios", tags=["👤 usuarios"])
app.include_router(administradores_router, prefix="/api/v1/administradores", tags=["👑 administradores"])
app.include_router(mascotas_router, prefix="/api/v1/mascotas", tags=["🐕 mascotas"])
app.include_router(catalogos_router, prefix="/api/v1/catalogos", tags=["📋 catálogos"])
app.include_router(consultas_router, prefix="/api/v1/consultas", tags=["🏥 consultas"])
app.include_router(triaje_router, prefix="/api/v1/triaje", tags=["🏥 Triaje"])
app.include_router(servicio_solicitado_router, prefix="/api/v1/servicio_solicitado", tags=["🏥 Servicio_solicitado"])
app.include_router(solicitudes_router, prefix="/api/v1/solicitudes", tags=["🏥 Solicitudes"])

@app.get("/")
async def root():
    return {"message": "API Operativa", "status": "OK"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

# ===== CORRECCIÓN DE ERRORES AQUÍ =====

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    # CORREGIDO: Devuelve JSONResponse, no un diccionario
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error de base de datos",
            "detail": "No se pudo conectar o ejecutar la operación en la base de datos.",
            "status_code": 500
        }
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    # CORREGIDO: Devuelve JSONResponse, no un diccionario
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint no encontrado",
            "detail": f"La ruta {request.url.path} no existe",
            "status_code": 404
        }
    )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, log_level="info")