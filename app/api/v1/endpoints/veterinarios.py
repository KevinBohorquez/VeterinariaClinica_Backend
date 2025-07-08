# app/api/v1/endpoints/veterinarios.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.config.database import get_db
# ✅ TEMPORAL: Usar el patrón que funciona en clientes
from app.crud import veterinario  # ← Si existe este import
from app.models import ResultadoServicio, Cita, ServicioSolicitado
from app.models.veterinario import Veterinario
from app.models.especialidad import Especialidad
from app.schemas import VeterinarioResponse, VeterinarioCreate, VeterinarioUpdate

# from app.schemas.veterinario_schema import (...)  # ← Comentado temporalmente

router = APIRouter()


@router.get("/")
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
    try:
        skip = (page - 1) * per_page

        query = db.query(Veterinario)

        # Aplicar filtros opcionales
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinarios: {str(e)}"
        )


@router.get("/{veterinario_id}")
async def get_veterinario(
        veterinario_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener un veterinario específico por ID
    """
    try:
        veterinario_obj = db.query(Veterinario).filter(Veterinario.id_veterinario == veterinario_id).first()

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinario: {str(e)}"
        )


@router.get("/dni/{dni}")
async def get_veterinario_by_dni(
        dni: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por DNI
    """
    try:
        if len(dni) != 8 or not dni.isdigit():
            raise HTTPException(
                status_code=400,
                detail="DNI debe tener exactamente 8 dígitos"
            )

        veterinario_obj = db.query(Veterinario).filter(Veterinario.dni == dni).first()

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar veterinario: {str(e)}"
        )


@router.get("/email/{email}")
async def get_veterinario_by_email(
        email: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por email
    """
    try:
        veterinario_obj = db.query(Veterinario).filter(Veterinario.email == email).first()

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar veterinario: {str(e)}"
        )


@router.get("/codigo-cmvp/{codigo_cmvp}")
async def get_veterinario_by_codigo_cmvp(
        codigo_cmvp: str,
        db: Session = Depends(get_db)
):
    """
    Obtener veterinario por código CMVP
    """
    try:
        veterinario_obj = db.query(Veterinario).filter(Veterinario.codigo_CMVP == codigo_cmvp).first()

        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veterinario no encontrado"
            )

        return veterinario_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar veterinario: {str(e)}"
        )


@router.get("/disponibles")
async def get_veterinarios_disponibles(
        db: Session = Depends(get_db),
        turno: Optional[str] = Query(None, description="Filtrar por turno"),
        especialidad_id: Optional[int] = Query(None, description="Filtrar por ID de especialidad")
):
    """
    Obtener veterinarios disponibles (disposicion = 'Libre')
    """
    try:
        query = db.query(Veterinario).filter(Veterinario.disposicion == "Libre")

        if turno:
            query = query.filter(Veterinario.turno == turno)
        if especialidad_id:
            query = query.filter(Veterinario.id_especialidad == especialidad_id)

        veterinarios = query.all()

        return {
            "veterinarios_disponibles": veterinarios,
            "total": len(veterinarios),
            "filtros": {
                "turno": turno,
                "especialidad_id": especialidad_id
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinarios disponibles: {str(e)}"
        )


@router.get("/especialidad/{especialidad_id}")
async def get_veterinarios_by_especialidad(
        especialidad_id: int,
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página")
):
    """
    Obtener veterinarios por ID de especialidad
    """
    try:
        skip = (page - 1) * per_page

        # Verificar que la especialidad existe
        especialidad_obj = db.query(Especialidad).filter(Especialidad.id_especialidad == especialidad_id).first()
        if not especialidad_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Especialidad no encontrada"
            )

        query = db.query(Veterinario).filter(Veterinario.id_especialidad == especialidad_id)

        total = query.count()
        veterinarios = query.offset(skip).limit(per_page).all()

        return {
            "especialidad": {
                "id": especialidad_obj.id_especialidad,
                "nombre": especialidad_obj.nombre
            },
            "veterinarios": veterinarios,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener veterinarios por especialidad: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=VeterinarioResponse)
async def create_veterinario(
        veterinario_data: VeterinarioCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo veterinario
    """
    try:
        # Verificar que la especialidad existe
        especialidad_obj = db.query(Especialidad).filter(
            Especialidad.id_especialidad == veterinario_data.id_especialidad
        ).first()

        if not especialidad_obj:
            raise HTTPException(
                status_code=404,
                detail="Especialidad no encontrada"
            )

        # Verificar duplicados DNI
        if veterinario.exists_by_dni(db, dni=veterinario_data.dni):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un veterinario con este DNI"
            )

        # Verificar duplicados email
        if veterinario.exists_by_email(db, email=veterinario_data.email):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un veterinario con este email"
            )

        # Verificar duplicados código CMVP
        if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=veterinario_data.codigo_CMVP):
            raise HTTPException(
                status_code=400,
                detail="Ya existe un veterinario con este código CMVP"
            )

        # Crear el veterinario
        nuevo_veterinario = veterinario.create(db, obj_in=veterinario_data)

        return nuevo_veterinario

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear veterinario: {str(e)}"
        )


@router.put("/{veterinario_id}", response_model=VeterinarioResponse)
async def update_veterinario(
        veterinario_id: int,
        veterinario_data: VeterinarioUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un veterinario existente
    """
    try:
        # Verificar que el veterinario existe
        veterinario_obj = veterinario.get(db, veterinario_id)
        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Verificar especialidad si se está actualizando
        if veterinario_data.id_especialidad:
            especialidad_obj = db.query(Especialidad).filter(
                Especialidad.id_especialidad == veterinario_data.id_especialidad
            ).first()

            if not especialidad_obj:
                raise HTTPException(
                    status_code=404,
                    detail="Especialidad no encontrada"
                )

        # Verificar email único si se está actualizando
        if veterinario_data.email:
            if veterinario.exists_by_email(db, email=veterinario_data.email, exclude_id=veterinario_id):
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe otro veterinario con este email"
                )

        # Verificar código CMVP único si se está actualizando
        if veterinario_data.codigo_CMVP:
            if veterinario.exists_by_codigo_cmvp(db, codigo_cmvp=veterinario_data.codigo_CMVP,
                                                 exclude_id=veterinario_id):
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe otro veterinario con este código CMVP"
                )

        # Actualizar el veterinario
        veterinario_actualizado = veterinario.update(db, db_obj=veterinario_obj, obj_in=veterinario_data)

        return veterinario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar veterinario: {str(e)}"
        )

@router.delete("/{veterinario_id}")
async def delete_veterinario(
    veterinario_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un veterinario
    """
    try:
        # Verificar que el veterinario existe
        veterinario_obj = veterinario.get(db, veterinario_id)
        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Verificar si el veterinario tiene citas pendientes o está ocupado
        if veterinario_obj.disposicion == "Ocupado":
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar un veterinario que está ocupado"
            )

        # Eliminar el veterinario
        veterinario.remove(db, id=veterinario_id)

        return {
            "message": "Veterinario eliminado exitosamente",
            "veterinario_id": veterinario_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar veterinario: {str(e)}"
        )


@router.put("/veterinario/usuario/{id_usuario}/disposicion", response_model=VeterinarioResponse)
async def update_veterinario_disposicion(
        id_usuario: int,
        db: Session = Depends(get_db)
):
    """
    Actualizar la disposición de un veterinario a 'Ocupado'
    """
    try:
        # Buscar al veterinario usando el id_usuario
        veterinario_obj = db.query(Veterinario).filter(Veterinario.id_usuario == id_usuario).first()

        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Crear objeto con los datos a actualizar
        disposicion_data = {"disposicion": "Ocupado"}

        # Actualizar el veterinario usando el patrón .update()
        veterinario_actualizado = veterinario.update(db, db_obj=veterinario_obj, obj_in=disposicion_data)

        return veterinario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar disposición: {str(e)}"
        )

@router.put("/veterinario/usuario/{id_usuario}/disposicionLibre", response_model=VeterinarioResponse)
async def update_veterinario_disposicion(
        id_usuario: int,
        db: Session = Depends(get_db)
):
    """
    Actualizar la disposición de un veterinario a 'Ocupado'
    """
    try:
        # Buscar al veterinario usando el id_usuario
        veterinario_obj = db.query(Veterinario).filter(Veterinario.id_usuario == id_usuario).first()

        if not veterinario_obj:
            raise HTTPException(
                status_code=404,
                detail="Veterinario no encontrado"
            )

        # Crear objeto con los datos a actualizar
        disposicion_data = {"disposicion": "Libre"}

        # Actualizar el veterinario usando el patrón .update()
        veterinario_actualizado = veterinario.update(db, db_obj=veterinario_obj, obj_in=disposicion_data)

        return veterinario_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar disposición: {str(e)}"
        )

@router.get("resultados-completos/{id_usuario}")
def get_resultados_completos_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    # Validar veterinario
    veterinario = db.query(Veterinario).filter(Veterinario.id_usuario == id_usuario).first()
    if not veterinario:
        raise HTTPException(status_code=404, detail="No se encontró el veterinario asociado a este usuario")

    # Traer todos los resultados con joins
    resultados = (
        db.query(ResultadoServicio)
        .join(ResultadoServicio.cita)
        .join(Cita.mascota)
        .join(Cita.servicio_solicitado)
        .join(ServicioSolicitado.servicio)
        .options(
            joinedload(ResultadoServicio.cita)
            .joinedload(Cita.mascota),
            joinedload(ResultadoServicio.cita)
            .joinedload(Cita.servicio_solicitado)
            .joinedload(ServicioSolicitado.servicio)
        )
        .filter(ResultadoServicio.id_veterinario == veterinario.id_veterinario)
        .all()
    )

    # Serializar
    resultado_list = []
    for r in resultados:
        cita = r.cita
        mascota = cita.mascota if cita else None
        servicio_solicitado = cita.servicio_solicitado if cita else None
        servicio = servicio_solicitado.servicio if servicio_solicitado else None

        resultado_dict = {
            "id_resultado": r.id_resultado,
            "id_cita": r.id_cita,
            "resultado": r.resultado,
            "interpretacion": r.interpretacion,
            "archivo_adjunto": r.archivo_adjunto,
            "fecha_realizacion": r.fecha_realizacion.isoformat() if r.fecha_realizacion else None,
            "cita": {
                "id_cita": cita.id_cita if cita else None,
                "fecha_hora_programada": cita.fecha_hora_programada.isoformat() if cita and cita.fecha_hora_programada else None,
                "estado_cita": cita.estado_cita if cita else None,
                "mascota": {
                    "id_mascota": mascota.id_mascota if mascota else None,
                    "nombre": mascota.nombre if mascota else None,
                    "sexo": mascota.sexo if mascota else None,
                    "color": mascota.color if mascota else None,
                } if mascota else None,
                "servicio": {
                    "id_servicio": servicio.id_servicio if servicio else None,
                    "nombre_servicio": servicio.nombre_servicio if servicio else None,
                    "precio": float(servicio.precio) if servicio else None
                } if servicio else None
            } if cita else None
        }

        resultado_list.append(resultado_dict)

    return resultado_list
