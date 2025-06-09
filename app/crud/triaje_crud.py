# app/crud/triaje_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Tuple
from datetime import datetime, date
from app.crud.base_crud import CRUDBase
from app.models.triaje import Triaje
from app.schemas.triaje_schema import TriajeCreate, TriajeUpdate, TriajeSearch
from datetime import datetime, timedelta


class CRUDTriaje(CRUDBase[Triaje, TriajeCreate, TriajeUpdate]):

    def get_by_solicitud(self, db: Session, *, id_solicitud: int) -> Optional[Triaje]:
        """Obtener triaje por ID de solicitud"""
        return db.query(Triaje).filter(Triaje.id_solicitud == id_solicitud).first()

    def get_by_veterinario(self, db: Session, *, id_veterinario: int, limit: int = 50) -> List[Triaje]:
        """Obtener triajes realizados por un veterinario"""
        return db.query(Triaje).filter(Triaje.id_veterinario == id_veterinario) \
            .order_by(desc(Triaje.fecha_hora_triaje)) \
            .limit(limit).all()

    def search_triajes(self, db: Session, *, search_params: TriajeSearch) -> Tuple[List[Triaje], int]:
        """Buscar triajes con filtros múltiples"""
        query = db.query(Triaje)

        # Aplicar filtros
        if search_params.id_veterinario:
            query = query.filter(Triaje.id_veterinario == search_params.id_veterinario)

        if search_params.clasificacion_urgencia:
            query = query.filter(Triaje.clasificacion_urgencia == search_params.clasificacion_urgencia)

        if search_params.condicion_corporal:
            query = query.filter(Triaje.condicion_corporal == search_params.condicion_corporal)

        if search_params.fecha_inicio:
            query = query.filter(Triaje.fecha_hora_triaje >= search_params.fecha_inicio)

        if search_params.fecha_fin:
            fecha_fin_complete = datetime.combine(search_params.fecha_fin, datetime.max.time())
            query = query.filter(Triaje.fecha_hora_triaje <= fecha_fin_complete)

        if search_params.peso_min:
            query = query.filter(Triaje.peso_mascota >= search_params.peso_min)

        if search_params.peso_max:
            query = query.filter(Triaje.peso_mascota <= search_params.peso_max)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenamiento
        triajes = query.order_by(desc(Triaje.fecha_hora_triaje)) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return triajes, total

    def get_by_urgencia(self, db: Session, *, clasificacion: str, limit: int = 20) -> List[Triaje]:
        """Obtener triajes por clasificación de urgencia"""
        return db.query(Triaje).filter(Triaje.clasificacion_urgencia == clasificacion) \
            .order_by(desc(Triaje.fecha_hora_triaje)) \
            .limit(limit).all()

    def get_criticos_recientes(self, db: Session, *, horas: int = 24) -> List[Triaje]:
        """Obtener triajes críticos de las últimas X horas"""
        fecha_limite = datetime.now() - timedelta(hours=horas)
        return db.query(Triaje).filter(
            and_(
                Triaje.clasificacion_urgencia == 'Critico',
                Triaje.fecha_hora_triaje >= fecha_limite
            )
        ).order_by(desc(Triaje.fecha_hora_triaje)).all()

    def get_estadisticas_urgencia(self, db: Session, *, fecha_inicio: Optional[date] = None,
                                  fecha_fin: Optional[date] = None) -> dict:
        """Obtener estadísticas por clasificación de urgencia"""
        query = db.query(Triaje)

        if fecha_inicio:
            query = query.filter(Triaje.fecha_hora_triaje >= fecha_inicio)
        if fecha_fin:
            fecha_fin_complete = datetime.combine(fecha_fin, datetime.max.time())
            query = query.filter(Triaje.fecha_hora_triaje <= fecha_fin_complete)

        # Contar por clasificación
        total = query.count()
        criticos = query.filter(Triaje.clasificacion_urgencia == 'Critico').count()
        muy_urgentes = query.filter(Triaje.clasificacion_urgencia == 'Muy urgente').count()
        urgentes = query.filter(Triaje.clasificacion_urgencia == 'Urgente').count()
        poco_urgentes = query.filter(Triaje.clasificacion_urgencia == 'Poco urgente').count()
        no_urgentes = query.filter(Triaje.clasificacion_urgencia == 'No urgente').count()

        return {
            "total": total,
            "criticos": criticos,
            "muy_urgentes": muy_urgentes,
            "urgentes": urgentes,
            "poco_urgentes": poco_urgentes,
            "no_urgentes": no_urgentes,
            "porcentajes": {
                "criticos": round((criticos / total * 100), 2) if total > 0 else 0,
                "muy_urgentes": round((muy_urgentes / total * 100), 2) if total > 0 else 0,
                "urgentes": round((urgentes / total * 100), 2) if total > 0 else 0,
                "poco_urgentes": round((poco_urgentes / total * 100), 2) if total > 0 else 0,
                "no_urgentes": round((no_urgentes / total * 100), 2) if total > 0 else 0
            }
        }

    def get_promedio_signos_vitales(self, db: Session, *, fecha_inicio: Optional[date] = None,
                                    fecha_fin: Optional[date] = None) -> dict:
        """Obtener promedios de signos vitales"""
        from sqlalchemy import func

        query = db.query(
            func.avg(Triaje.peso_mascota).label('peso_promedio'),
            func.avg(Triaje.latido_por_minuto).label('latidos_promedio'),
            func.avg(Triaje.frecuencia_respiratoria_rpm).label('respiracion_promedio'),
            func.avg(Triaje.temperatura).label('temperatura_promedio'),
            func.avg(Triaje.frecuencia_pulso).label('pulso_promedio')
        )

        if fecha_inicio:
            query = query.filter(Triaje.fecha_hora_triaje >= fecha_inicio)
        if fecha_fin:
            fecha_fin_complete = datetime.combine(fecha_fin, datetime.max.time())
            query = query.filter(Triaje.fecha_hora_triaje <= fecha_fin_complete)

        result = query.first()

        return {
            "peso_promedio": float(result.peso_promedio) if result.peso_promedio else 0,
            "latidos_promedio": float(result.latidos_promedio) if result.latidos_promedio else 0,
            "respiracion_promedio": float(result.respiracion_promedio) if result.respiracion_promedio else 0,
            "temperatura_promedio": float(result.temperatura_promedio) if result.temperatura_promedio else 0,
            "pulso_promedio": float(result.pulso_promedio) if result.pulso_promedio else 0
        }

    def exists_for_solicitud(self, db: Session, *, id_solicitud: int) -> bool:
        """Verificar si ya existe un triaje para una solicitud"""
        return db.query(Triaje).filter(Triaje.id_solicitud == id_solicitud).first() is not None

    def get_triajes_by_date_range(self, db: Session, *, fecha_inicio: date, fecha_fin: date) -> List[Triaje]:
        """Obtener triajes en un rango de fechas"""
        fecha_fin_complete = datetime.combine(fecha_fin, datetime.max.time())
        return db.query(Triaje).filter(
            and_(
                Triaje.fecha_hora_triaje >= fecha_inicio,
                Triaje.fecha_hora_triaje <= fecha_fin_complete
            )
        ).order_by(desc(Triaje.fecha_hora_triaje)).all()


# Instancia única
triaje = CRUDTriaje(Triaje)