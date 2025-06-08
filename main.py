# main.py (LIMPIO - SIN DUPLICADOS)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from datetime import datetime

from app.config.database import get_db
from app.models.veterinaria import Cliente

app = FastAPI(
    title="🏥 Sistema Veterinaria API - Solo Clientes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🏥 Sistema Veterinaria API funcionando!",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "status": "OK - Solo Clientes"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Probar conexión a la base de datos"""
    try:
        result = db.execute("SELECT 1 as test").fetchone()
        return {
            "status": "success",
            "message": "Conexión exitosa",
            "test_result": "OK"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/clientes")
async def get_clientes(limit: int = 20, db: Session = Depends(get_db)):
    """Obtener clientes usando modelo simple"""
    try:
        clientes = db.query(Cliente).limit(limit).all()

        result = []
        for cliente in clientes:
            result.append({
                "id_cliente": cliente.id_cliente,
                "nombre": cliente.nombre,
                "apellido_paterno": cliente.apellido_paterno,
                "apellido_materno": cliente.apellido_materno,
                "dni": cliente.dni,
                "telefono": cliente.telefono,
                "email": cliente.email,
                "direccion": cliente.direccion,
                "estado": cliente.estado,
                "fecha_registro": cliente.fecha_registro.isoformat() if cliente.fecha_registro else None
            })

        return {
            "clientes": result,
            "total": len(result),
            "message": f"Se encontraron {len(result)} clientes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/clientes/{cliente_id}")
async def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente específico"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()

        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return {
            "id_cliente": cliente.id_cliente,
            "nombre": cliente.nombre,
            "apellido_paterno": cliente.apellido_paterno,
            "apellido_materno": cliente.apellido_materno,
            "dni": cliente.dni,
            "telefono": cliente.telefono,
            "email": cliente.email,
            "direccion": cliente.direccion,
            "estado": cliente.estado,
            "fecha_registro": cliente.fecha_registro.isoformat() if cliente.fecha_registro else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Estadísticas simples"""
    try:
        total_clientes = db.query(Cliente).count()
        clientes_activos = db.query(Cliente).filter(Cliente.estado == "Activo").count()

        return {
            "total_clientes": total_clientes,
            "clientes_activos": clientes_activos,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")