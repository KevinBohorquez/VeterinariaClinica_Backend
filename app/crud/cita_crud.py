# app/crud/cita_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Tuple
from datetime import datetime, date
from app.crud.base_crud import CRUDBase
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.cita import Cita
from app.models.resultado_servicio import ResultadoServicio
from app.schemas.consulta_schema import (
    ServicioSolicitadoCreate, CitaCreate, CitaUpdate, CitaSearch,
    ResultadoServicioCreate
)

# ===== SERVICIO SOLICITADO =====
class CRUDServicioSolicitado(CRUDBase[ServicioSolicitado, ServicioSolicitadoCreate, None]):
    
    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[ServicioSolicitado]:
        """Obtener servicios solicitados de una consulta"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_consulta == consulta_id).all()

    def get_by_servicio(self, db: Session, *, servicio_id: int) -> List[ServicioSolicitado]:
        """Obtener solicitudes de un servicio específico"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.id_servicio == servicio_id).all()

    def get_by_prioridad(self, db: Session, *, prioridad: str) -> List[ServicioSolicitado]:
        """Obtener servicios por prioridad"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.prioridad == prioridad).all()

    def get_pendientes(self, db: Session) -> List[ServicioSolicitado]:
        """Obtener servicios pendientes de programar"""
        return db.query(ServicioSolicitado).filter(ServicioSolicitado.estado_examen == "Solicitado").all()

    def cambiar_estado(self, db: Session, *, servicio_solicitado_id: int, nuevo_estado: str) -> Optional[ServicioSolicitado]:
        """Cambiar estado del servicio solicitado"""
        servicio_sol = self.get(db, servicio_solicitado_id)
        if servicio_sol:
            servicio_sol.estado_examen = nuevo_estado
            db.commit()
            db.refresh(servicio_sol)
        return servicio_sol

# ===== CITA =====
class CRUDCita(CRUDBase[Cita, CitaCreate, CitaUpdate]):
    
    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[Cita]:
        """Obtener citas de una mascota"""
        return db.query(Cita).filter(Cita.id_mascota == mascota_id)\
                            .order_by(desc(Cita.fecha_hora_programada)).all()

    def get_by_servicio(self, db: Session, *, servicio_id: int) -> List[Cita]:
        """Obtener citas de un servicio"""
        return db.query(Cita).filter(Cita.id_servicio == servicio_id).all()

    def get_by_fecha(self, db: Session, *, fecha: date) -> List[Cita]:
        """Obtener citas de una fecha específica"""
        return db.query(Cita).filter(
            db.func.date(Cita.fecha_hora_programada) == fecha
        ).order_by(Cita.fecha_hora_programada).all()

    def get_by_rango_fechas(self, db: Session, *, fecha_inicio: date, fecha_fin: date) -> List[Cita]:
        """Obtener citas en un rango de fechas"""
        return db.query(Cita).filter(
            and_(
                Cita.fecha_hora_programada >= fecha_inicio,
                Cita.fecha_hora_programada <= fecha_fin
            )
        ).order_by(Cita.fecha_hora_programada).all()

    def get_programadas(self, db: Session) -> List[Cita]:
        """Obtener citas programadas"""
        return db.query(Cita).filter(Cita.estado_cita == "Programada")\
                            .order_by(Cita.fecha_hora_programada).all()

    def get_pendientes_hoy(self, db: Session) -> List[Cita]:
        """Obtener citas programadas para hoy"""
        today = date.today()
        return db.query(Cita).filter(
            and_(
                db.func.date(Cita.fecha_hora_programada) == today,
                Cita.estado_cita == "Programada"
            )
        ).order_by(Cita.fecha_hora_programada).all()

    def search_citas(self, db: Session, *, search_params: CitaSearch) -> Tuple[List[Cita], int]:
        """Buscar citas con filtros"""
        query = db.query(Cita)
        
        if search_params.id_mascota:
            query = query.filter(Cita.id_mascota == search_params.id_mascota)
        
        if search_params.id_servicio:
            query = query.filter(Cita.id_servicio == search_params.id_servicio)
        
        if search_params.estado_cita:
            query = query.filter(Cita.estado_cita == search_params.estado_cita)
        
        if search_params.fecha_desde:
            query = query.filter(Cita.fecha_hora_programada >= search_params.fecha_desde)
        
        if search_params.fecha_hasta:
            query = query.filter(Cita.fecha_hora_programada <= search_params.fecha_hasta)
        
        total = query.count()
        
        citas = query.order_by(desc(Cita.fecha_hora_programada))\
                    .offset((search_params.page - 1) * search_params.per_page)\
                    .limit(search_params.per_page).all()
        
        return citas, total

    def verificar_disponibilidad(self, db: Session, *, fecha_hora: datetime, servicio_id: int) -> bool:
        """Verificar si hay disponibilidad para una cita"""
        # Verificar si ya existe una cita en esa fecha/hora para ese servicio
        existing_cita = db.query(Cita).filter(
            and_(
                Cita.fecha_hora_programada == fecha_hora,
                Cita.id_servicio == servicio_id,
                Cita.estado_cita == "Programada"
            )
        ).first()
        
        return existing_cita is None

    def cancelar_cita(self, db: Session, *, cita_id: int) -> Optional[Cita]:
        """Cancelar una cita"""
        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.estado_cita = "Cancelada"
            db.commit()
            db.refresh(cita)
        return cita

    def marcar_atendida(self, db: Session, *, cita_id: int) -> Optional[Cita]:
        """Marcar cita como atendida"""
        cita = self.get(db, cita_id)
        if cita and cita.estado_cita == "Programada":
            cita.estado_cita = "Atendida"
            db.commit()
            db.refresh(cita)
        return cita

# ===== RESULTADO SERVICIO =====
class CRUDResultadoServicio(CRUDBase[ResultadoServicio, ResultadoServicioCreate, None]):
    
    def get_by_cita(self, db: Session, *, cita_id: int) -> Optional[ResultadoServicio]:
        """Obtener resultado de una cita"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.id_cita == cita_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[ResultadoServicio]:
        """Obtener resultados realizados por un veterinario"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.id_veterinario == veterinario_id)\
                                         .order_by(desc(ResultadoServicio.fecha_realizacion)).all()

    def get_by_fecha(self, db: Session, *, fecha: date) -> List[ResultadoServicio]:
        """Obtener resultados de una fecha"""
        return db.query(ResultadoServicio).filter(
            db.func.date(ResultadoServicio.fecha_realizacion) == fecha
        ).all()

    def get_with_archivo(self, db: Session) -> List[ResultadoServicio]:
        """Obtener resultados que tienen archivo adjunto"""
        return db.query(ResultadoServicio).filter(ResultadoServicio.archivo_adjunto.isnot(None)).all()

# Instancias únicas
servicio_solicitado = CRUDServicioSolicitado(ServicioSolicitado)
cita = CRUDCita(Cita)
resultado_servicio = CRUDResultadoServicio(ResultadoServicio)