from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db

from app.models import Cita, ServicioSolicitado

from app.schemas.consulta_schema import (
    ServicioSolicitadoUpdate, ServicioSolicitadoResponse
)

router = APIRouter()

@router.get("/", response_model=List[ServicioSolicitadoResponse])
async def get_servicios_solicitados(db: Session = Depends(get_db)):
    """
    Obtener todos los servicios solicitados
    """
    try:
        servicios = db.query(ServicioSolicitado).all()
        return servicios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener servicios solicitados: {str(e)}")


# 1. Obtener todos los servicios solicitados que tienen citas
@router.get("/pendientes", response_model=List[ServicioSolicitadoResponse])
async def get_servicios_solicitados_pendientes(db: Session = Depends(get_db)):
    """
    Obtener todos los servicios solicitados que tienen citas asociadas
    Equivale a: SELECT * FROM Cita c INNER JOIN Servicio_Solicitado ON c.id_servicio_solicitado = Servicio_Solicitado.id_servicio_solicitado
    """
    try:
        servicios_con_cita = db.query(ServicioSolicitado) \
            .join(Cita, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .all()

        return servicios_con_cita

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener servicios solicitados con citas: {str(e)}")


# 2. Obtener un servicio solicitado específico que tenga cita
@router.get("/pendientes/{id_servicio_solicitado}", response_model=ServicioSolicitadoResponse)
async def get_servicio_solicitado_pendiente_por_id(id_servicio_solicitado: int, db: Session = Depends(get_db)):
    """
    Obtener un servicio solicitado específico que tenga cita asociada
    """
    try:
        servicio_con_cita = db.query(ServicioSolicitado) \
            .join(Cita, Cita.id_servicio_solicitado == ServicioSolicitado.id_servicio_solicitado) \
            .filter(ServicioSolicitado.id_servicio_solicitado == id_servicio_solicitado) \
            .first()

        if not servicio_con_cita:
            raise HTTPException(
                status_code=404,
                detail="Servicio solicitado no encontrado o no tiene cita asociada"
            )

        return servicio_con_cita

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener servicio solicitado: {str(e)}")

@router.put("/id_servicio_solicitado}", response_model=ServicioSolicitadoResponse)
async def update_servicio_solicitado(id_servicio_solicitado: int, servicio_solicitado: ServicioSolicitadoUpdate, db: Session = Depends(get_db)):
    """
    Actualizar un servicio solicitado
    """
    try:
        servicio = db.query(ServicioSolicitado).filter(ServicioSolicitado.id_servicio_solicitado == id_servicio_solicitado).first()

        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio solicitado no encontrado")

        # Actualizar los campos del servicio
        for key, value in servicio_solicitado.dict(exclude_unset=True).items():
            setattr(servicio, key, value)

        db.commit()
        db.refresh(servicio)

        return servicio
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar servicio solicitado: {str(e)}")
