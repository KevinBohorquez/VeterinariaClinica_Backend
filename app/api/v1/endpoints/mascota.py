# app/api/v1/endpoints/mascotas.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.crud import mascota, cliente
from app.models.mascota import Mascota  # ✅ Importar el modelo directamente
from app.schemas import (
    MascotaCreate, MascotaUpdate, MascotaResponse,
    MascotaWithDetailsResponse, MascotaListResponse, 
    MascotaSearch, MessageResponse
)
from app.api.deps import get_mascota_or_404

router = APIRouter()

@router.post("/", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
async def create_mascota(
    mascota_data: MascotaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva mascota
    """
    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, mascota_data.id_cliente)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente no existe"
        )
    
    # Verificar que la raza existe
    from app.crud import raza
    raza_obj = raza.get(db, mascota_data.id_raza)
    if not raza_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Raza no existe"
        )
    
    return mascota.create(db, obj_in=mascota_data)

@router.get("/", response_model=MascotaListResponse)
async def get_mascotas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo")
):
    """
    Obtener lista de mascotas con paginación
    """
    skip = (page - 1) * per_page
    
    query = db.query(Mascota)  # ✅ Usar Mascota directamente
    
    if cliente_id:
        query = query.filter(Mascota.id_cliente == cliente_id)
    
    if sexo:
        query = query.filter(Mascota.sexo == sexo)
    
    total = query.count()
    mascotas = query.offset(skip).limit(per_page).all()
    
    return {
        "mascotas": mascotas,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/{mascota_id}", response_model=MascotaResponse)
async def get_mascota(
    mascota_obj: Mascota = Depends(get_mascota_or_404)  # ✅ CORRECTO
):
    """
    Obtener una mascota específica por ID
    """
    return mascota_obj

@router.get("/{mascota_id}/details", response_model=MascotaWithDetailsResponse)
async def get_mascota_with_details(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener mascota con detalles del cliente y raza
    """
    details = mascota.get_with_details(db, mascota_id=mascota_id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )
    
    return {
        **details["mascota"].__dict__,
        "cliente_nombre": details["cliente_nombre_completo"],
        "raza_nombre": details["raza_nombre"]
    }

@router.put("/{mascota_id}", response_model=MascotaResponse)
async def update_mascota(
    mascota_id: int,
    mascota_data: MascotaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una mascota
    """
    # Verificar que existe
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )
    
    # Validar raza si se está actualizando
    update_data = mascota_data.dict(exclude_unset=True)
    if "id_raza" in update_data:
        from app.crud import raza
        raza_obj = raza.get(db, update_data["id_raza"])
        if not raza_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Raza no existe"
            )
    
    return mascota.update(db, db_obj=mascota_obj, obj_in=mascota_data)

@router.delete("/{mascota_id}", response_model=MessageResponse)
async def delete_mascota(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar una mascota
    """
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )
    
    mascota.remove(db, id=mascota_id)
    return {"message": "Mascota eliminada correctamente", "success": True}

@router.post("/search", response_model=MascotaListResponse)
async def search_mascotas(
    search_params: MascotaSearch,
    db: Session = Depends(get_db)
):
    """
    Buscar mascotas con filtros avanzados
    """
    mascotas_result, total = mascota.search_mascotas(db, search_params=search_params)
    
    return {
        "mascotas": mascotas_result,
        "total": total,
        "page": search_params.page,
        "per_page": search_params.per_page,
        "total_pages": (total + search_params.per_page - 1) // search_params.per_page
    }

@router.get("/cliente/{cliente_id}/list")
async def get_mascotas_by_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las mascotas de un cliente específico
    """
    # Verificar que el cliente existe
    cliente_obj = cliente.get(db, cliente_id)
    if not cliente_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    
    mascotas = mascota.get_mascotas_by_cliente(db, cliente_id=cliente_id)
    
    return {
        "cliente_id": cliente_id,
        "cliente_nombre": f"{cliente_obj.nombre} {cliente_obj.apellido_paterno}",
        "mascotas": mascotas,
        "total": len(mascotas)
    }

@router.get("/stats/por-sexo")
async def get_estadisticas_por_sexo(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de mascotas por sexo
    """
    stats = mascota.count_mascotas_by_sexo(db)
    return {
        "estadisticas_por_sexo": stats,
        "total": stats["machos"] + stats["hembras"]
    }

@router.get("/no-esterilizadas/list")
async def get_mascotas_no_esterilizadas(
    db: Session = Depends(get_db)
):
    """
    Obtener mascotas no esterilizadas
    """
    mascotas = mascota.get_mascotas_no_esterilizadas(db)
    return {
        "mascotas_no_esterilizadas": mascotas,
        "total": len(mascotas)
    }

@router.get("/{mascota_id}/historial")
async def get_historial_mascota(
    mascota_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener historial clínico de una mascota
    """
    # Verificar que la mascota existe
    mascota_obj = mascota.get(db, mascota_id)
    if not mascota_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mascota no encontrada"
        )
    
    from app.crud import historial_clinico
    historial = historial_clinico.get_by_mascota(db, mascota_id=mascota_id)
    
    return {
        "mascota": {
            "id": mascota_obj.id_mascota,
            "nombre": mascota_obj.nombre
        },
        "historial": historial,
        "total_eventos": len(historial)
    }