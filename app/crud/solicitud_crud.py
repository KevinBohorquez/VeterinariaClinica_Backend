# app/crud/solicitud_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from app.crud.base_crud import CRUDBase
from app.models.solicitud_atencion import SolicitudAtencion
from app.schemas.solicitud_schema import SolicitudCreate, SolicitudUpdate, SolicitudSearch


class CRUDSolicitud(CRUDBase[SolicitudAtencion, SolicitudCreate, SolicitudUpdate]):

    def get_by_mascota(self, db: Session, *, id_mascota: int, limit: int = 50) -> List[SolicitudAtencion]:
        """Obtener solicitudes por mascota"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_mascota == id_mascota) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)) \
            .limit(limit).all()

    def get_by_recepcionista(self, db: Session, *, id_recepcionista: int, limit: int = 50) -> List[SolicitudAtencion]:
        """Obtener solicitudes registradas por una recepcionista"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_recepcionista == id_recepcionista) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)) \
            .limit(limit).all()

    def get_by_estado(self, db: Session, *, estado: str, limit: int = 100) -> List[SolicitudAtencion]:
        """Obtener solicitudes por estado"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == estado) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)) \
            .limit(limit).all()

    def get_by_tipo(self, db: Session, *, tipo_solicitud: str, limit: int = 100) -> List[SolicitudAtencion]:
        """Obtener solicitudes por tipo"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.tipo_solicitud == tipo_solicitud) \
            .order_by(desc(SolicitudAtencion.fecha_hora_solicitud)) \
            .limit(limit).all()

    def search_solicitudes(self, db: Session, *, search_params: SolicitudSearch) -> Tuple[List[SolicitudAtencion], int]:
        """Buscar solicitudes con filtros múltiples"""
        query = db.query(SolicitudAtencion)

        # Aplicar filtros
        if search_params.id_mascota:
            query = query.filter(SolicitudAtencion.id_mascota == search_params.id_mascota)

        if search_params.id_recepcionista:
            query = query.filter(SolicitudAtencion.id_recepcionista == search_params.id_recepcionista)

        if search_params.tipo_solicitud:
            query = query.filter(SolicitudAtencion.tipo_solicitud == search_params.tipo_solicitud)

        if search_params.estado:
            query = query.filter(SolicitudAtencion.estado == search_params.estado)

        if search_params.fecha_inicio:
            query = query.filter(SolicitudAtencion.fecha_hora_solicitud >= search_params.fecha_inicio)

        if search_params.fecha_fin:
            fecha_fin_complete = datetime.combine(search_params.fecha_fin, datetime.max.time())
            query = query.filter(SolicitudAtencion.fecha_hora_solicitud <= fecha_fin_complete)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenamiento
        solicitudes = query.order_by(desc(SolicitudAtencion.fecha_hora_solicitud)) \
            .offset((search_params.page - 1) * search_params.per_page) \
            .limit(search_params.per_page).all()

        return solicitudes, total

    def get_pendientes(self, db: Session, *, limit: int = 50) -> List[SolicitudAtencion]:
        """Obtener solicitudes pendientes"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == 'Pendiente') \
            .order_by(SolicitudAtencion.fecha_hora_solicitud) \
            .limit(limit).all()

    def get_urgentes_pendientes(self, db: Session, *, limit: int = 20) -> List[SolicitudAtencion]:
        """Obtener solicitudes urgentes pendientes"""
        return db.query(SolicitudAtencion).filter(
            and_(
                SolicitudAtencion.tipo_solicitud == 'Consulta urgente',
                SolicitudAtencion.estado.in_(['Pendiente', 'En triaje'])
            )
        ).order_by(SolicitudAtencion.fecha_hora_solicitud).limit(limit).all()

    def get_en_proceso(self, db: Session, *, limit: int = 50) -> List[SolicitudAtencion]:
        """Obtener solicitudes en proceso (En triaje o En atención)"""
        return db.query(SolicitudAtencion).filter(
            SolicitudAtencion.estado.in_(['En triaje', 'En atencion'])
        ).order_by(SolicitudAtencion.fecha_hora_solicitud).limit(limit).all()

    def cambiar_estado(self, db: Session, *, id_solicitud: int, nuevo_estado: str) -> Optional[SolicitudAtencion]:
        """Cambiar el estado de una solicitud"""
        solicitud_obj = db.query(SolicitudAtencion).filter(SolicitudAtencion.id_solicitud == id_solicitud).first()
        if solicitud_obj:
            solicitud_obj.estado = nuevo_estado
            db.commit()
            db.refresh(solicitud_obj)
        return solicitud_obj

    def get_estadisticas_por_estado(self, db: Session, *, fecha_inicio: Optional[date] = None,
                                    fecha_fin: Optional[date] = None) -> dict:
        """Obtener estadísticas por estado"""
        query = db.query(SolicitudAtencion)

        if fecha_inicio:
            query = query.filter(SolicitudAtencion.fecha_hora_solicitud >= fecha_inicio)
        if fecha_fin:
            fecha_fin_complete = datetime.combine(fecha_fin, datetime.max.time())
            query = query.filter(SolicitudAtencion.fecha_hora_solicitud <= fecha_fin_complete)

        # Contar por estado
        total = query.count()
        pendientes = query.filter(SolicitudAtencion.estado == 'Pendiente').count()
        en_triaje = query.filter(SolicitudAtencion.estado == 'En triaje').count()
        en_atencion = query.filter(SolicitudAtencion.estado == 'En atencion').count()
        completadas = query.filter(SolicitudAtencion.estado == 'Completada').count()
        canceladas = query.filter(SolicitudAtencion.estado == 'Cancelada').count()

        return {
            "total": total,
            "pendientes": pendientes,
            "en_triaje": en_triaje,
            "en_atencion": en_atencion,
            "completadas": completadas,
            "canceladas": canceladas,
            "porcentajes": {
                "pendientes": round((pendientes / total * 100), 2) if total > 0 else 0,
                "en_triaje": round((en_triaje / total * 100), 2) if total > 0 else 0,
                "en_atencion": round((en_atencion / total * 100), 2) if total > 0 else 0,
                "completadas": round((completadas / total * 100), 2) if total > 0 else 0,
                "canceladas": round((canceladas / total * 100), 2) if total > 0 else 0
            }
        }

    def get_estadisticas_por_tipo(self, db: Session, *, fecha_inicio: Optional[date] = None,
                                  fecha_fin: Optional[date] = None) -> dict:
        """Obtener estadísticas por tipo de solicitud"""
        query = db.query(SolicitudAtencion)

        if fecha_inicio:
            query = query.filter(SolicitudAtencion.fecha_hora_solicitud >= fecha_inicio)
        if fecha_fin:
            fecha_fin_complete = datetime.combine(fecha_fin, datetime.max.time())
            query = query.filter(SolicitudAtencion.fecha_hora_solicitud <= fecha_fin_complete)

        # Contar por tipo
        total = query.count()
        urgentes = query.filter(SolicitudAtencion.tipo_solicitud == 'Consulta urgente').count()
        normales = query.filter(SolicitudAtencion.tipo_solicitud == 'Consulta normal').count()
        programadas = query.filter(SolicitudAtencion.tipo_solicitud == 'Servicio programado').count()

        return {
            "total": total,
            "consultas_urgentes": urgentes,
            "consultas_normales": normales,
            "servicios_programados": programadas,
            "porcentajes": {
                "urgentes": round((urgentes / total * 100), 2) if total > 0 else 0,
                "normales": round((normales / total * 100), 2) if total > 0 else 0,
                "programadas": round((programadas / total * 100), 2) if total > 0 else 0
            }
        }

    def get_solicitudes_by_date_range(self, db: Session, *, fecha_inicio: date, fecha_fin: date) -> List[
        SolicitudAtencion]:
        """Obtener solicitudes en un rango de fechas"""
        fecha_fin_complete = datetime.combine(fecha_fin, datetime.max.time())
        return db.query(SolicitudAtencion).filter(
            and_(
                SolicitudAtencion.fecha_hora_solicitud >= fecha_inicio,
                SolicitudAtencion.fecha_hora_solicitud <= fecha_fin_complete
            )
        ).order_by(desc(SolicitudAtencion.fecha_hora_solicitud)).all()

    def get_resumen_diario(self, db: Session, *, fecha: date) -> dict:
        """Obtener resumen de solicitudes del día"""
        fecha_inicio = datetime.combine(fecha, datetime.min.time())
        fecha_fin = datetime.combine(fecha, datetime.max.time())

        query = db.query(SolicitudAtencion).filter(
            and_(
                SolicitudAtencion.fecha_hora_solicitud >= fecha_inicio,
                SolicitudAtencion.fecha_hora_solicitud <= fecha_fin
            )
        )

        total_dia = query.count()
        urgentes_dia = query.filter(SolicitudAtencion.tipo_solicitud == 'Consulta urgente').count()
        pendientes_dia = query.filter(SolicitudAtencion.estado == 'Pendiente').count()
        completadas_dia = query.filter(SolicitudAtencion.estado == 'Completada').count()

        return {
            "fecha": fecha,
            "total": total_dia,
            "urgentes": urgentes_dia,
            "pendientes": pendientes_dia,
            "completadas": completadas_dia,
            "tasa_completion": round((completadas_dia / total_dia * 100), 2) if total_dia > 0 else 0
        }


# Instancia única
solicitud = CRUDSolicitud(SolicitudAtencion)