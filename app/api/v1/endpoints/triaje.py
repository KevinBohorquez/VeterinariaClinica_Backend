# app/api/v1/endpoints/triajes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.config.database import get_db
from app.crud.triaje_crud import triaje
from app.models.triaje import Triaje
from app.schemas.triaje_schema import (
    TriajeCreate, TriajeUpdate, TriajeResponse,
    TriajeListResponse, TriajeSearch, EstadisticasUrgencia, PromediosSignosVitales
)

router = APIRouter()


@router.post("/", response_model=TriajeResponse, status_code=status.HTTP_201_CREATED)
async def create_triaje(
        triaje_data: TriajeCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un nuevo triaje
    """
    try:
        # Verificar que no existe ya un triaje para esta solicitud
        if triaje.exists_for_solicitud(db, id_solicitud=triaje_data.id_solicitud):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un triaje para esta solicitud"
            )

        # Verificar que la solicitud existe
        from app.crud.solicitud_crud import solicitud
        solicitud_obj = solicitud.get(db, triaje_data.id_solicitud)
        if not solicitud_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solicitud no encontrada"
            )

        # Verificar que el veterinario existe
        from app.crud.veterinario_crud import veterinario
        veterinario_obj = veterinario.get(db, triaje_data.id_veterinario)
        if not veterinario_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Veterinario no encontrado"
            )

        # Agregar timestamp actual
        triaje_data_dict = triaje_data.dict()
        triaje_data_dict['fecha_hora_triaje'] = datetime.now()

        return triaje.create(db, obj_in=triaje_data_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear triaje: {str(e)}"
        )


@router.get("/", response_model=TriajeListResponse)
async def get_triajes(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        clasificacion_urgencia: Optional[str] = Query(None, description="Filtrar por clasificación"),
        id_veterinario: Optional[int] = Query(None, description="Filtrar por veterinario")
):
    """
    Obtener lista de triajes con paginación
    """
    try:
        skip = (page - 1) * per_page

        query = db.query(Triaje)

        if clasificacion_urgencia:
            query = query.filter(Triaje.clasificacion_urgencia == clasificacion_urgencia)
        if id_veterinario:
            query = query.filter(Triaje.id_veterinario == id_veterinario)

        total = query.count()
        triajes = query.order_by(Triaje.fecha_hora_triaje.desc()) \
            .offset(skip) \
            .limit(per_page) \
            .all()

        return {
            "triajes": triajes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triajes: {str(e)}"
        )


@router.get("/{triaje_id}", response_model=TriajeResponse)
async def get_triaje(
        triaje_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtener un triaje específico por ID
    """
    try:
        triaje_obj = triaje.get(db, triaje_id)
        if not triaje_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triaje no encontrado"
            )
        return triaje_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triaje: {str(e)}"
        )


@router.put("/{triaje_id}", response_model=TriajeResponse)
async def update_triaje(
        triaje_id: int,
        triaje_data: TriajeUpdate,
        db: Session = Depends(get_db)
):
    """
    Actualizar un triaje
    """
    try:
        triaje_obj = triaje.get(db, triaje_id)
        if not triaje_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triaje no encontrado"
            )

        return triaje.update(db, db_obj=triaje_obj, obj_in=triaje_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar triaje: {str(e)}"
        )


@router.delete("/{triaje_id}")
async def delete_triaje(
        triaje_id: int,
        db: Session = Depends(get_db)
):
    """
    Eliminar un triaje
    """
    try:
        triaje_obj = triaje.get(db, triaje_id)
        if not triaje_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Triaje no encontrado"
            )

        triaje.remove(db, id=triaje_id)
        return {
            "message": "Triaje eliminado correctamente",
            "success": True,
            "triaje_id": triaje_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar triaje: {str(e)}"
        )


@router.post("/search", response_model=TriajeListResponse)
async def search_triajes(
        search_params: TriajeSearch,
        db: Session = Depends(get_db)
):
    """
    Buscar triajes con filtros avanzados
    """
    try:
        triajes_result, total = triaje.search_triajes(db, search_params=search_params)

        return {
            "triajes": triajes_result,
            "total": total,
            "page": search_params.page,
            "per_page": search_params.per_page,
            "total_pages": (total + search_params.per_page - 1) // search_params.per_page
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda de triajes: {str(e)}"
        )


@router.get("/solicitud/{id_solicitud}", response_model=TriajeResponse)
async def get_triaje_by_solicitud(
        id_solicitud: int,
        db: Session = Depends(get_db)
):
    """
    Obtener triaje por ID de solicitud
    """
    try:
        triaje_obj = triaje.get_by_solicitud(db, id_solicitud=id_solicitud)
        if not triaje_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró triaje para esta solicitud"
            )
        return triaje_obj

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar triaje por solicitud: {str(e)}"
        )


@router.get("/veterinario/{id_veterinario}")
async def get_triajes_by_veterinario(
        id_veterinario: int,
        db: Session = Depends(get_db),
        limit: int = Query(50, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener triajes realizados por un veterinario
    """
    try:
        triajes_list = triaje.get_by_veterinario(db, id_veterinario=id_veterinario, limit=limit)

        return {
            "id_veterinario": id_veterinario,
            "triajes": triajes_list,
            "total": len(triajes_list)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triajes del veterinario: {str(e)}"
        )


@router.get("/urgencia/{clasificacion}")
async def get_triajes_by_urgencia(
        clasificacion: str,
        db: Session = Depends(get_db),
        limit: int = Query(20, ge=1, le=100, description="Límite de resultados")
):
    """
    Obtener triajes por clasificación de urgencia
    """
    try:
        urgencias_validas = ['No urgente', 'Poco urgente', 'Urgente', 'Muy urgente', 'Critico']
        if clasificacion not in urgencias_validas:
            raise HTTPException(
                status_code=400,
                detail=f"Clasificación debe ser una de: {', '.join(urgencias_validas)}"
            )

        triajes_list = triaje.get_by_urgencia(db, clasificacion=clasificacion, limit=limit)

        return {
            "clasificacion_urgencia": clasificacion,
            "triajes": triajes_list,
            "total": len(triajes_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triajes por urgencia: {str(e)}"
        )


@router.get("/criticos/recientes")
async def get_triajes_criticos_recientes(
        db: Session = Depends(get_db),
        horas: int = Query(24, ge=1, le=168, description="Últimas X horas")
):
    """
    Obtener triajes críticos recientes
    """
    try:
        triajes_criticos = triaje.get_criticos_recientes(db, horas=horas)

        return {
            "triajes_criticos": triajes_criticos,
            "total": len(triajes_criticos),
            "periodo_horas": horas
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triajes críticos: {str(e)}"
        )


@router.get("/estadisticas/urgencia")
async def get_estadisticas_urgencia(
        db: Session = Depends(get_db),
        fecha_inicio: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
        fecha_fin: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    """
    Obtener estadísticas por clasificación de urgencia
    """
    try:
        stats = triaje.get_estadisticas_urgencia(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/estadisticas/signos-vitales")
async def get_promedios_signos_vitales(
        db: Session = Depends(get_db),
        fecha_inicio: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
        fecha_fin: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    """
    Obtener promedios de signos vitales
    """
    try:
        promedios = triaje.get_promedio_signos_vitales(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        return promedios

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener promedios de signos vitales: {str(e)}"
        )


@router.get("/rango-fechas")
async def get_triajes_by_date_range(
        db: Session = Depends(get_db),
        fecha_inicio: date = Query(..., description="Fecha inicio (YYYY-MM-DD)"),
        fecha_fin: date = Query(..., description="Fecha fin (YYYY-MM-DD)")
):
    """
    Obtener triajes en un rango de fechas
    """
    try:
        if fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )

        triajes_list = triaje.get_triajes_by_date_range(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

        return {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "triajes": triajes_list,
            "total": len(triajes_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener triajes por rango de fechas: {str(e)}"
        )


@router.get("/dashboard/resumen")
async def get_dashboard_triajes(
        db: Session = Depends(get_db)
):
    """
    Obtener resumen para dashboard de triajes
    """
    try:
        from datetime import timedelta

        hoy = date.today()
        hace_7_dias = hoy - timedelta(days=7)
        hace_30_dias = hoy - timedelta(days=30)

        # Estadísticas generales
        total_triajes = db.query(Triaje).count()
        triajes_hoy = db.query(Triaje).filter(
            Triaje.fecha_hora_triaje >= datetime.combine(hoy, datetime.min.time())
        ).count()

        # Triajes críticos recientes
        criticos_24h = triaje.get_criticos_recientes(db, horas=24)

        # Estadísticas de urgencia última semana
        stats_semana = triaje.get_estadisticas_urgencia(db, fecha_inicio=hace_7_dias, fecha_fin=hoy)

        # Promedios signos vitales último mes
        promedios_mes = triaje.get_promedio_signos_vitales(db, fecha_inicio=hace_30_dias, fecha_fin=hoy)

        return {
            "resumen_general": {
                "total_triajes": total_triajes,
                "triajes_hoy": triajes_hoy,
                "criticos_ultimas_24h": len(criticos_24h)
            },
            "estadisticas_semana": stats_semana,
            "promedios_signos_vitales_mes": promedios_mes,
            "triajes_criticos_recientes": criticos_24h[:5],  # Solo los 5 más recientes
            "fecha_consulta": hoy
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener dashboard: {str(e)}"
        )