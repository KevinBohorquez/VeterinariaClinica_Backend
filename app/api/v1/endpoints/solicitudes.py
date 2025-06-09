# app/api/v1/endpoints/solicitudes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.config.database import get_db
from app.crud.solicitud_crud import solicitud
from app.models.solicitud_atencion import SolicitudAtencion
from app.schemas.solicitud_schema import (
    SolicitudCreate, SolicitudUpdate, SolicitudResponse,
    SolicitudListResponse, SolicitudSearch, SolicitudWithDetailsResponse,
    EstadisticasSolicitud, EstadisticasTipo, ResumenDiario, CambioEstado, FlujoSolicitud
)

router = APIRouter()


@router.post("/", response_model=SolicitudResponse, status_code=status.HTTP_201_CREATED)
async def create_solicitud(
        solicitud_data: SolicitudCreate,
        db: Session = Depends(get_db)
):
    """
    Crear una nueva solicitud de atención
    """
    try:
        # Verificar que la mascota existe
        from app.crud.mascota_crud import mascota
        mascota_obj = mascota.get(db, solicitud_data.id_mascota)
        if not mascota_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mascota no encontrada"
            )

        # Verificar que la recepcionista existe
        from app.crud.recepcionistas_crud import recepcionista
        recepcionista_obj = recepcionista.get(db, solicitud_data.id_recepcionista)
        if not recepcionista_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recepcionista no encontrada"
            )

        # Agregar timestamp actual
        solicitud_data_dict = solicitud_data.dict()
        solicitud_data_dict['fecha_hora_solicitud'] = datetime.now()

        return solicitud.create(db, obj_in=solicitud_data_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear solicitud: {str(e)}"
        )


@router.get("/", response_model=SolicitudListResponse)
async def get_solicitudes(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        estado: Optional[str] = Query(None, description="Filtrar por estado"),
        tipo_solicitud: Optional[str] = Query(None, description="Filtrar por tipo"),
        id_mascota: Optional[int] = Query(None, description="Filtrar por mascota"),
        id_recepcionista: Optional[int] = Query(None, description="Filtrar por recepcionista")
):
    """
    Obtener lista de solicitudes con paginación
    """
    try:
        skip = (page - 1) * per_page

        query = db.query(SolicitudAtencion)

        if estado:
            query = query.filter(SolicitudAtencion.estado == estado)
        if tipo_solicitud:
            query = query.filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud)
        if id_mascota:
            query = query.filter(SolicitudAtencion.id_mascota == id_mascota)
        if id_recepcionista:
            query = query.filter(SolicitudAtencion.id_recepcionista == id_recepcionista)

        total = query.count()
        solicitudes = query.order_by(SolicitudAtencion.fecha_hora_solicitud.desc()) \
            .offset(skip) \
            .limit(per_page) \
            .all()

        return {
            "solicitudes": solicitudes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )


@router.get("/{solicitud_id}", response_model=SolicitudResponse)
async def get_solicitud(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener una solicitud específica por ID
    """
    try:
        solicitud_obj = solicitud.get(db, solicitud_id)
        if not solicitud_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )
        return solicitud_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitud: {str(e)}"
        )


@router.put("/{solicitud_id}", response_model=SolicitudResponse)
async def update_solicitud(
        solicitud_id: int,
        solicitud_data: SolicitudUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar una solicitud
    """
    try:
        solicitud_obj = solicitud.get(db, solicitud_id)
        if not solicitud_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )

        return solicitud.update(db, db_obj=solicitud_obj, obj_in=solicitud_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar solicitud: {str(e)}"
        )


@router.delete("/{solicitud_id}")
async def delete_solicitud(
        solicitud_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar una solicitud
    """
    try:
        solicitud_obj = solicitud.get(db, solicitud_id)
        if not solicitud_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )

        solicitud.remove(db, id=solicitud_id)
        return {
            "message": "Solicitud eliminada correctamente",
            "success": True,
            "solicitud_id": solicitud_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar solicitud: {str(e)}"
        )


@router.post("/search", response_model=SolicitudListResponse)
async def search_solicitudes(
        search_params: SolicitudSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar solicitudes con filtros avanzados
    """
    try:
        solicitudes_result, total = solicitud.search_solicitudes(db, search_params=search_params)

        return {
            "solicitudes": solicitudes_result,
            "total": total,
            "page": search_params.page,
            "per_page": search_params.per_page,
            "total_pages": (total + search_params.per_page - 1) // search_params.per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de solicitudes: {str(e)}"
        )


@router.patch("/{solicitud_id}/estado")
async def cambiar_estado_solicitud(
        solicitud_id: int,
        cambio_estado: CambioEstado,
        db: Session = Depends(get_db)
):
    """
    Cambiar el estado de una solicitud
    """
    try:
        solicitud_obj = solicitud.cambiar_estado(db, id_solicitud=solicitud_id, nuevo_estado=cambio_estado.nuevo_estado)
        if not solicitud_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )

        return {
            "message": f"Estado cambiado a {cambio_estado.nuevo_estado}",
            "solicitud": solicitud_obj,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al cambiar estado: {str(e)}"
        )


@router.get("/mascota/{id_mascota}")
async def get_solicitudes_by_mascota(
        id_mascota: int,
        db: Session = Depends(get_db),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener solicitudes de una mascota específica
    """
    try:
        solicitudes_list = solicitud.get_by_mascota(db, id_mascota=id_mascota, limit=limit)

        return {
            "id_mascota": id_mascota,
            "solicitudes": solicitudes_list,
            "total": len(solicitudes_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes de mascota: {str(e)}"
        )


@router.get("/recepcionista/{id_recepcionista}")
async def get_solicitudes_by_recepcionista(
        id_recepcionista: int,
        db: Session = Depends(get_db),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener solicitudes registradas por una recepcionista
    """
    try:
        solicitudes_list = solicitud.get_by_recepcionista(db, id_recepcionista=id_recepcionista, limit=limit)

        return {
            "id_recepcionista": id_recepcionista,
            "solicitudes": solicitudes_list,
            "total": len(solicitudes_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener solicitudes de recepcionista: {str(e)}"
        )