# app/api/v1/endpoints/recepcionistas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud.recepcionistas_crud import recepcionista  # ✅ Siguiendo tu patrón
from app.models.recepcionista import Recepcionista  # ✅ Importar el modelo directamente
from app.schemas.recepcionista_schema import (  # ✅ Siguiendo tu patrón
    RecepcionistaCreate, RecepcionistaUpdate, RecepcionistaResponse,
    RecepcionistaListResponse, RecepcionistaSearch
)
# from app.api.deps import get_recepcionista_or_404, validate_pagination  # ← Comentado hasta crear deps

router = APIRouter()

@router.post("/", response_model=RecepcionistaResponse, status_code=status.HTTP_201_CREATED)
async def create_recepcionista(
    recepcionista_data: RecepcionistaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva recepcionista
    """
    # Validar duplicados
    if recepcionista.exists_by_dni(db, dni=recepcionista_data.dni):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una recepcionista con ese DNI"
        )

    if recepcionista.exists_by_email(db, email=recepcionista_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una recepcionista con ese email"
        )

    return recepcionista.create(db, obj_in=recepcionista_data)

@router.get("/", response_model=RecepcionistaListResponse)
async def get_recepcionistas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    turno: Optional[str] = Query(None, description="Filtrar por turno"),
    genero: Optional[str] = Query(None, description="Filtrar por género")
):
    """
    Obtener lista de recepcionistas con paginación
    """
    skip = (page - 1) * per_page

    query = db.query(Recepcionista)  # ✅ Usar Recepcionista directamente
    if estado:
        query = query.filter(Recepcionista.estado == estado)
    if turno:
        query = query.filter(Recepcionista.turno == turno)
    if genero:
        query = query.filter(Recepcionista.genero == genero)

    total = query.count()
    recepcionistas = query.offset(skip).limit(per_page).all()

    return {
        "recepcionistas": recepcionistas,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/{recepcionista_id}", response_model=RecepcionistaResponse)
async def get_recepcionista(
    recepcionista_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener una recepcionista específica por ID
    """
    recepcionista_obj = recepcionista.get(db, recepcionista_id)
    if not recepcionista_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recepcionista no encontrada"
        )
    return recepcionista_obj

@router.put("/{recepcionista_id}", response_model=RecepcionistaResponse)
async def update_recepcionista(
    recepcionista_id: int,
    recepcionista_data: RecepcionistaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una recepcionista
    """
    # Verificar que existe
    recepcionista_obj = recepcionista.get(db, recepcionista_id)
    if not recepcionista_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recepcionista no encontrada"
        )

    # Validar duplicados si se están actualizando
    update_data = recepcionista_data.dict(exclude_unset=True)

    if "dni" in update_data:
        if recepcionista.exists_by_dni(db, dni=update_data["dni"], exclude_id=recepcionista_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una recepcionista con ese DNI"
            )

    if "email" in update_data:
        if recepcionista.exists_by_email(db, email=update_data["email"], exclude_id=recepcionista_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una recepcionista con ese email"
            )

    return recepcionista.update(db, db_obj=recepcionista_obj, obj_in=recepcionista_data)

@router.delete("/{recepcionista_id}")
async def delete_recepcionista(
    recepcionista_id: int,
    db: Session = Depends(get_db),
    permanent: bool = Query(False, description="Eliminación permanente")
):
    """
    Eliminar una recepcionista (soft delete por defecto)
    """
    recepcionista_obj = recepcionista.get(db, recepcionista_id)
    if not recepcionista_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recepcionista no encontrada"
        )

    if permanent:
        recepcionista.remove(db, id=recepcionista_id)
        message = "Recepcionista eliminada permanentemente"
    else:
        recepcionista.soft_delete(db, id=recepcionista_id)
        message = "Recepcionista desactivada"

    return {
        "message": message,
        "success": True,
        "recepcionista_id": recepcionista_id
    }

@router.post("/search", response_model=RecepcionistaListResponse)
async def search_recepcionistas(
    search_params: RecepcionistaSearch,
    db: Session = Depends(get_db)
):
    """
    Buscar recepcionistas con filtros avanzados
    """
    recepcionistas_result, total = recepcionista.search_recepcionistas(db, search_params=search_params)

    return {
        "recepcionistas": recepcionistas_result,
        "total": total,
        "page": search_params.page,
        "per_page": search_params.per_page,
        "total_pages": (total + search_params.per_page - 1) // search_params.per_page
    }

@router.get("/dni/{dni}", response_model=RecepcionistaResponse)
async def get_recepcionista_by_dni(
    dni: str,
    db: Session = Depends(get_db)
):
    """
    Obtener recepcionista por DNI
    """
    recepcionista_obj = recepcionista.get_by_dni(db, dni=dni)
    if not recepcionista_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recepcionista no encontrada"
        )
    return recepcionista_obj

@router.get("/email/{email}", response_model=RecepcionistaResponse)
async def get_recepcionista_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Obtener recepcionista por email
    """
    recepcionista_obj = recepcionista.get_by_email(db, email=email)
    if not recepcionista_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recepcionista no encontrada"
        )
    return recepcionista_obj

@router.get("/turno/{turno}")
async def get_recepcionistas_by_turno(
    turno: str,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
    estado: Optional[str] = Query("Activo", description="Filtrar por estado")
):
    """
    Obtener recepcionistas por turno
    """
    skip = (page - 1) * per_page

    query = db.query(Recepcionista).filter(Recepcionista.turno == turno)

    if estado:
        query = query.filter(Recepcionista.estado == estado)

    total = query.count()
    recepcionistas = query.offset(skip).limit(per_page).all()

    return {
        "turno": turno,
        "estado_filtro": estado,
        "recepcionistas": recepcionistas,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/activas")
async def get_recepcionistas_activas(
    db: Session = Depends(get_db),
    turno: Optional[str] = Query(None, description="Filtrar por turno")
):
    """
    Obtener recepcionistas activas
    """
    query = db.query(Recepcionista).filter(Recepcionista.estado == "Activo")

    if turno:
        query = query.filter(Recepcionista.turno == turno)

    recepcionistas = query.all()

    return {
        "recepcionistas_activas": recepcionistas,
        "total": len(recepcionistas),
        "filtros": {
            "turno": turno
        }
    }

@router.patch("/{recepcionista_id}/estado")
async def cambiar_estado_recepcionista(
    recepcionista_id: int,
    nuevo_estado: str = Query(..., description="Nuevo estado: Activo o Inactivo"),
    db: Session = Depends(get_db)
):
    """
    Cambiar el estado de una recepcionista
    """
    if nuevo_estado not in ["Activo", "Inactivo"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado debe ser 'Activo' o 'Inactivo'"
        )

    recepcionista_obj = recepcionista.get(db, recepcionista_id)
    if not recepcionista_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recepcionista no encontrada"
        )

    recepcionista_obj.estado = nuevo_estado
    db.commit()
    db.refresh(recepcionista_obj)

    return {
        "message": f"Estado cambiado a {nuevo_estado}",
        "recepcionista": recepcionista_obj,
        "success": True
    }