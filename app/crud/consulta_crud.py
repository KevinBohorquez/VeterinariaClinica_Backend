# app/crud/consulta_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Tuple
from datetime import datetime, date
from app.crud.base_crud import CRUDBase
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje
from app.models.consulta import Consulta
from app.models.diagnostico import Diagnostico
from app.models.tratamiento import Tratamiento
from app.models.historial_clinico import HistorialClinico
from app.schemas.consulta_schema import (
    SolicitudAtencionCreate, TriajeCreate, ConsultaCreate,
    DiagnosticoCreate, TratamientoCreate, HistorialClinicoCreate,
    ConsultaSearch, HistorialSearch
)

# ===== SOLICITUD ATENCIÓN =====
class CRUDSolicitudAtencion(CRUDBase[SolicitudAtencion, SolicitudAtencionCreate, None]):
    
    def get_by_mascota(self, db: Session, *, mascota_id: int) -> List[SolicitudAtencion]:
        """Obtener solicitudes por mascota"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.id_mascota == mascota_id).all()

    def get_pendientes(self, db: Session) -> List[SolicitudAtencion]:
        """Obtener solicitudes pendientes"""
        return db.query(SolicitudAtencion).filter(SolicitudAtencion.estado == "Pendiente").all()

    def cambiar_estado(self, db: Session, *, solicitud_id: int, nuevo_estado: str) -> Optional[SolicitudAtencion]:
        """Cambiar estado de la solicitud"""
        solicitud = self.get(db, solicitud_id)
        if solicitud:
            solicitud.estado = nuevo_estado
            db.commit()
            db.refresh(solicitud)
        return solicitud

# ===== TRIAJE =====
class CRUDTriaje(CRUDBase[Triaje, TriajeCreate, None]):
    
    def get_by_solicitud(self, db: Session, *, solicitud_id: int) -> Optional[Triaje]:
        """Obtener triaje por solicitud"""
        return db.query(Triaje).filter(Triaje.id_solicitud == solicitud_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int) -> List[Triaje]:
        """Obtener triajes realizados por un veterinario"""
        return db.query(Triaje).filter(Triaje.id_veterinario == veterinario_id).all()

    def get_by_urgencia(self, db: Session, *, clasificacion: str) -> List[Triaje]:
        """Obtener triajes por nivel de urgencia"""
        return db.query(Triaje).filter(Triaje.clasificacion_urgencia == clasificacion).all()

    def get_criticos(self, db: Session) -> List[Triaje]:
        """Obtener casos críticos"""
        return db.query(Triaje).filter(Triaje.clasificacion_urgencia == "Critico").all()

# ===== CONSULTA =====
class CRUDConsulta(CRUDBase[Consulta, ConsultaCreate, None]):
    
    def get_by_triaje(self, db: Session, *, triaje_id: int) -> Optional[Consulta]:
        """Obtener consulta por triaje"""
        return db.query(Consulta).filter(Consulta.id_triaje == triaje_id).first()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int, fecha_inicio: date = None, fecha_fin: date = None) -> List[Consulta]:
        """Obtener consultas por veterinario en un rango de fechas"""
        query = db.query(Consulta).filter(Consulta.id_veterinario == veterinario_id)
        
        if fecha_inicio:
            query = query.filter(Consulta.fecha_consulta >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Consulta.fecha_consulta <= fecha_fin)
        
        return query.order_by(desc(Consulta.fecha_consulta)).all()

    def search_consultas(self, db: Session, *, search_params: ConsultaSearch) -> Tuple[List[Consulta], int]:
        """Buscar consultas con filtros"""
        query = db.query(Consulta)
        
        if search_params.id_veterinario:
            query = query.filter(Consulta.id_veterinario == search_params.id_veterinario)
        
        if search_params.fecha_desde:
            query = query.filter(Consulta.fecha_consulta >= search_params.fecha_desde)
        
        if search_params.fecha_hasta:
            query = query.filter(Consulta.fecha_consulta <= search_params.fecha_hasta)
        
        if search_params.condicion_general:
            query = query.filter(Consulta.condicion_general == search_params.condicion_general)
        
        if search_params.es_seguimiento is not None:
            query = query.filter(Consulta.es_seguimiento == search_params.es_seguimiento)
        
        total = query.count()
        
        consultas = query.order_by(desc(Consulta.fecha_consulta))\
                        .offset((search_params.page - 1) * search_params.per_page)\
                        .limit(search_params.per_page).all()
        
        return consultas, total

    def get_seguimientos(self, db: Session) -> List[Consulta]:
        """Obtener consultas de seguimiento"""
        return db.query(Consulta).filter(Consulta.es_seguimiento == True).all()

# ===== DIAGNÓSTICO =====
class CRUDDiagnostico(CRUDBase[Diagnostico, DiagnosticoCreate, None]):
    
    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[Diagnostico]:
        """Obtener diagnósticos de una consulta"""
        return db.query(Diagnostico).filter(Diagnostico.id_consulta == consulta_id).all()

    def get_by_patologia(self, db: Session, *, patologia_id: int) -> List[Diagnostico]:
        """Obtener diagnósticos por patología"""
        return db.query(Diagnostico).filter(Diagnostico.id_patologia == patologia_id).all()

    def get_confirmados(self, db: Session) -> List[Diagnostico]:
        """Obtener diagnósticos confirmados"""
        return db.query(Diagnostico).filter(Diagnostico.tipo_diagnostico == "Confirmado").all()

# ===== TRATAMIENTO =====
class CRUDTratamiento(CRUDBase[Tratamiento, TratamientoCreate, None]):
    
    def get_by_consulta(self, db: Session, *, consulta_id: int) -> List[Tratamiento]:
        """Obtener tratamientos de una consulta"""
        return db.query(Tratamiento).filter(Tratamiento.id_consulta == consulta_id).all()

    def get_by_tipo(self, db: Session, *, tipo_tratamiento: str) -> List[Tratamiento]:
        """Obtener tratamientos por tipo"""
        return db.query(Tratamiento).filter(Tratamiento.tipo_tratamiento == tipo_tratamiento).all()

    def get_activos(self, db: Session) -> List[Tratamiento]:
        """Obtener tratamientos activos (iniciados recientemente)"""
        return db.query(Tratamiento).filter(Tratamiento.fecha_inicio <= date.today()).all()

# ===== HISTORIAL CLÍNICO =====
class CRUDHistorialClinico(CRUDBase[HistorialClinico, HistorialClinicoCreate, None]):
    
    def get_by_mascota(self, db: Session, *, mascota_id: int, limit: int = 50) -> List[HistorialClinico]:
        """Obtener historial clínico de una mascota"""
        return db.query(HistorialClinico)\
               .filter(HistorialClinico.id_mascota == mascota_id)\
               .order_by(desc(HistorialClinico.fecha_evento))\
               .limit(limit).all()

    def search_historial(self, db: Session, *, search_params: HistorialSearch) -> Tuple[List[HistorialClinico], int]:
        """Buscar en historial clínico"""
        query = db.query(HistorialClinico).filter(HistorialClinico.id_mascota == search_params.id_mascota)
        
        if search_params.tipo_evento:
            query = query.filter(HistorialClinico.tipo_evento.ilike(f"%{search_params.tipo_evento}%"))
        
        if search_params.fecha_desde:
            query = query.filter(HistorialClinico.fecha_evento >= search_params.fecha_desde)
        
        if search_params.fecha_hasta:
            query = query.filter(HistorialClinico.fecha_evento <= search_params.fecha_hasta)
        
        total = query.count()
        
        historial = query.order_by(desc(HistorialClinico.fecha_evento))\
                        .offset((search_params.page - 1) * search_params.per_page)\
                        .limit(search_params.per_page).all()
        
        return historial, total

    def add_evento(self, db: Session, *, evento_data: HistorialClinicoCreate) -> HistorialClinico:
        """Agregar evento al historial"""
        evento_data.fecha_evento = evento_data.fecha_evento or datetime.now()
        return self.create(db, obj_in=evento_data)

# Instancias únicas
solicitud_atencion = CRUDSolicitudAtencion(SolicitudAtencion)
triaje = CRUDTriaje(Triaje)
consulta = CRUDConsulta(Consulta)
diagnostico = CRUDDiagnostico(Diagnostico)
tratamiento = CRUDTratamiento(Tratamiento)
historial_clinico = CRUDHistorialClinico(HistorialClinico)