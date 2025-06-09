# app/api/v1/endpoints/veterinarios.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud import veterinario
from app.models.veterinario import Veterinario  # ✅ Importar el modelo directamente
from app.models.especialidad import Especialidad
from app.schemas import (
    VeterinarioCreate, VeterinarioUpdate, VeterinarioResponse,
    VeterinarioListResponse, VeterinarioSearch, MessageResponse
)
from app.api.deps import get_veterinario_or_404, validate_pagination

router = APIRouter()


@router.post("/", response_model=VeterinarioResponse, status_code=status.HTTP_201_CREATED)
async def create_veterinario(
        veterinario_data: VeterinarioCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo veterinario
    """
    # Validar duplicados
    if veterinario.exists_by_dni(db, dni=veterinario_data.dni):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un veterinario con ese DNI"
        )

    if veterinario.exists_by_email(db, email=veterinario_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un veterinario con ese email"
        )

    if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=veterinario_data.codigo_CMVP):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un veterinario con ese código CMVP"
        )

    return veterinario.create(db, obj_in=veterinario_data)


@router.get("/", response_model=VeterinarioListResponse)
async def get_veterinarios(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),

        especialidad: Optional[str] = Query(None, description="Filtrar por especialidad"),
        tipo_veterinario: Optional[str] = Query(None, description="Filtrar por tipo de veterinario"),
        disposicion: Optional[str] = Query(None, description="Filtrar por disposición"),
        turno: Optional[str] = Query(None, description="Filtrar por turno")
):
    """
    Obtener lista de veterinarios con paginación
    """
    skip = (page - 1) * per_page

    query = db.query(Veterinario)  # ✅ Usar Veterinario directamente
    if especialidad:
        query = query.join(Veterinario.especialidad).filter(Especialidad.nombre.ilike(f"%{especialidad}%"))
    if tipo_veterinario:
        query = query.filter(Veterinario.tipo_veterinario == tipo_veterinario)
    if disposicion:
        query = query.filter(Veterinario.disposicion == disposicion)
    if turno:
        query = query.filter(Veterinario.turno == turno)

    total = query.count()
    veterinarios = query.offset(skip).limit(per_page).all()

    return {
        "veterinarios": veterinarios,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/{veterinario_id}", response_model=VeterinarioResponse)
async def get_veterinario(
        veterinario_obj: Veterinario = Depends(get_veterinario_or_404)  # ✅ CORRECTO
):
    """
    Obtener un veterinario específico por ID
    """
    return veterinario_obj


@router.put("/{veterinario_id}", response_model=VeterinarioResponse)
async def update_veterinario(
        veterinario_id: int,
        veterinario_data: VeterinarioUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un veterinario
    """
    # Verificar que existe
    veterinario_obj = veterinario.get(db, veterinario_id)
    if not veterinario_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )

    # Validar duplicados si se están actualizando
    update_data = veterinario_data.dict(exclude_unset=True)

    if "dni" in update_data:
        if veterinario.exists_by_dni(db, dni=update_data["dni"], exclude_id=veterinario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un veterinario con ese DNI"
            )

    if "email" in update_data:
        if veterinario.exists_by_email(db, email=update_data["email"], exclude_id=veterinario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un veterinario con ese email"
            )

    if "codigo_CMVP" in update_data:
        if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=update_data["codigo_CMVP"], exclude_id=veterinario_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un veterinario con ese código CMVP"
            )

    return veterinario.update(db, db_obj=veterinario_obj, obj_in=veterinario_data)


@router.delete("/{veterinario_id}", response_model=MessageResponse)
async def delete_veterinario(
        veterinario_id: int,
        db: Session = Depends(get_db),
        permanent: bool = Query(False, description="Eliminación permanente")
):
    """
    Eliminar un veterinario (soft delete por defecto)
    """
    veterinario_obj = veterinario.get(db, veterinario_id)
    if not veterinario_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )

    if permanent:
        veterinario.remove(db, id=veterinario_id)
        message = "Veterinario eliminado permanentemente"
    else:
        veterinario.soft_delete(db, id=veterinario_id)
        message = "Veterinario desactivado"

    return {"message": message, "success": True}


@router.post("/search", response_model=VeterinarioListResponse)
async def search_veterinarios(
        search_params: VeterinarioSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar veterinarios con filtros avanzados
    """
    veterinarios_result, total = veterinario.search_veterinarios(db, search_params=search_params)

    return {
        "veterinarios": veterinarios_result,
        "total": total,
        "page": search_params.page,
        "per_page": search_params.per_page,
        "total_pages": (total + search_params.per_page - 1) // search_params.per_page
    }


@router.get("/{veterinario_id}/citas")
async def get_citas_veterinario(
        veterinario_id: int,
        db: Session = Depends(get_db),
        fecha_inicio: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
        fecha_fin: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
        estado: Optional[str] = Query(None, description="Estado de la cita")
):
    """
    Obtener todas las citas de un veterinario
    """
    from app.crud import cita

    # Verificar que el veterinario existe
    veterinario_obj = veterinario.get(db, veterinario_id)
    if not veterinario_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )

    citas = cita.get_citas_by_veterinario(
        db,
        veterinario_id=veterinario_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=estado
    )

    return {
        "veterinario": {
            "id": veterinario_obj.id_veterinario,
            "nombre": f"Dr. {veterinario_obj.nombre} {veterinario_obj.apellido_paterno}",
            "especialidad": veterinario_obj.especialidad.nombre if veterinario_obj.especialidad else None
        },
        "citas": citas,
        "total_citas": len(citas)
    }


@router.get("/dni/{dni}", response_model=VeterinarioResponse)
async def get_veterinario_by_dni(
        dni: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por DNI
    """
    veterinario_obj = veterinario.get_by_dni(db, dni=dni)
    if not veterinario_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )
    return veterinario_obj


@router.get("/email/{email}", response_model=VeterinarioResponse)
async def get_veterinario_by_email(
        email: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por email
    """
    veterinario_obj = veterinario.get_by_email(db, email=email)
    if not veterinario_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )
    return veterinario_obj


@router.get("/codigo-cmvp/{codigo_cmvp}", response_model=VeterinarioResponse)
async def get_veterinario_by_codigo_cmvp(
        codigo_cmvp: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por código CMVP
    """
    veterinario_obj = veterinario.get_by_codigo_cmvp(db, codigo_cmvp=codigo_cmvp)
    if not veterinario_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado"
        )
    return veterinario_obj


@router.get("/especialidad/{especialidad}")
async def get_veterinarios_by_especialidad(
        especialidad: str,
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    Obtener veterinarios por especialidad
    """
    skip = (page - 1) * per_page

    query = db.query(Veterinario).filter(
        Veterinario.especialidad.ilike(f"%{especialidad}%"),
        Veterinario.estado == "activo"
    )

    total = query.count()
    veterinarios = query.offset(skip).limit(per_page).all()

    return {
        "especialidad": especialidad,
        "veterinarios": veterinarios,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }