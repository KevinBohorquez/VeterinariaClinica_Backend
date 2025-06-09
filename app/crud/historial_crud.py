# app/crud/historial_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, timedelta
from app.crud.base_crud import CRUDBase
from app.models.historial_clinico import HistorialClinico
from app.schemas.consulta_schema import HistorialClinicoCreate, HistorialSearch


class CRUDHistorialClinico(CRUDBase[HistorialClinico, HistorialClinicoCreate, None]):

    def get_by_mascota(self, db: Session, *, mascota_id: int, limit: int = 50) -> List[HistorialClinico]:
        """Obtener historial clínico de una mascota ordenado por fecha"""
        return db.query(HistorialClinico)\
               .filter(HistorialClinico.id_mascota == mascota_id)\
               .order_by(desc(HistorialClinico.fecha_evento))\
               .limit(limit).all()

    def get_by_veterinario(self, db: Session, *, veterinario_id: int, limit: int = 100) -> List[HistorialClinico]:
        """Obtener eventos del historial realizados por un veterinario"""
        return db.query(HistorialClinico)\
               .filter(HistorialClinico.id_veterinario == veterinario_id)\
               .order_by(desc(HistorialClinico.fecha_evento))\
               .limit(limit).all()

    def search_historial(self, db: Session, *, search_params: HistorialSearch) -> Tuple[List[HistorialClinico], int]:
        """Buscar en historial clínico con filtros"""
        query = db.query(HistorialClinico).filter(HistorialClinico.id_mascota == search_params.id_mascota)
        
        if search_params.tipo_evento:
            query = query.filter(HistorialClinico.tipo_evento.ilike(f"%{search_params.tipo_evento}%"))
        
        if search_params.fecha_desde:
            query = query.filter(HistorialClinico.fecha_evento >= search_params.fecha_desde)
        
        if search_params.fecha_hasta:
            fecha_hasta_complete = datetime.combine(search_params.fecha_hasta, datetime.max.time())
            query = query.filter(HistorialClinico.fecha_evento <= fecha_hasta_complete)
        
        total = query.count()
        
        historial = query.order_by(desc(HistorialClinico.fecha_evento))\
                        .offset((search_params.page - 1) * search_params.per_page)\
                        .limit(search_params.per_page).all()
        
        return historial, total

    def add_evento(self, db: Session, *, evento_data: HistorialClinicoCreate) -> HistorialClinico:
        """Agregar evento al historial con timestamp automático"""
        evento_dict = evento_data.dict()
        evento_dict['fecha_evento'] = evento_dict.get('fecha_evento', datetime.now())
        
        evento = HistorialClinico(**evento_dict)
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return evento

    def get_eventos_por_tipo(self, db: Session, *, mascota_id: int, tipo_evento: str) -> List[HistorialClinico]:
        """Obtener eventos de un tipo específico para una mascota"""
        return db.query(HistorialClinico)\
               .filter(
                   and_(
                       HistorialClinico.id_mascota == mascota_id,
                       HistorialClinico.tipo_evento.ilike(f"%{tipo_evento}%")
                   )
               )\
               .order_by(desc(HistorialClinico.fecha_evento)).all()

    def get_eventos_recientes(self, db: Session, *, mascota_id: int, dias: int = 30) -> List[HistorialClinico]:
        """Obtener eventos recientes de una mascota"""
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        return db.query(HistorialClinico)\
               .filter(
                   and_(
                       HistorialClinico.id_mascota == mascota_id,
                       HistorialClinico.fecha_evento >= fecha_limite
                   )
               )\
               .order_by(desc(HistorialClinico.fecha_evento)).all()

    def get_historial_completo_mascota(self, db: Session, *, mascota_id: int) -> Dict[str, Any]:
        """Obtener historial completo de una mascota con información relacionada"""
        from app.models.mascota import Mascota
        from app.models.consulta import Consulta
        from app.models.diagnostico import Diagnostico
        from app.models.tratamiento import Tratamiento
        from app.models.veterinario import Veterinario
        
        # Información básica de la mascota
        mascota = db.query(Mascota).filter(Mascota.id_mascota == mascota_id).first()
        if not mascota:
            return {}
        
        # Todos los eventos del historial
        eventos = self.get_by_mascota(db, mascota_id=mascota_id, limit=1000)
        
        # Estadísticas
        total_eventos = len(eventos)
        tipos_eventos = db.query(
            HistorialClinico.tipo_evento,
            func.count(HistorialClinico.id_historial).label('total')
        ).filter(HistorialClinico.id_mascota == mascota_id)\
         .group_by(HistorialClinico.tipo_evento).all()
        
        # Eventos por veterinario
        eventos_por_vet = db.query(
            Veterinario.nombre,
            Veterinario.apellido_paterno,
            func.count(HistorialClinico.id_historial).label('total_eventos')
        ).join(Veterinario, HistorialClinico.id_veterinario == Veterinario.id_veterinario)\
         .filter(HistorialClinico.id_mascota == mascota_id)\
         .group_by(Veterinario.id_veterinario, Veterinario.nombre, Veterinario.apellido_paterno).all()
        
        return {
            "mascota_info": {
                "id_mascota": mascota.id_mascota,
                "nombre": mascota.nombre,
                "sexo": mascota.sexo,
                "edad_anios": mascota.edad_anios,
                "edad_meses": mascota.edad_meses
            },
            "eventos": eventos,
            "estadisticas": {
                "total_eventos": total_eventos,
                "tipos_eventos": [
                    {"tipo": t.tipo_evento, "total": t.total} for t in tipos_eventos
                ],
                "eventos_por_veterinario": [
                    {
                        "veterinario": f"{v.nombre} {v.apellido_paterno}",
                        "total_eventos": v.total_eventos
                    } for v in eventos_por_vet
                ]
            }
        }

    def get_eventos_por_consulta(self, db: Session, *, consulta_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a una consulta específica"""
        return db.query(HistorialClinico)\
               .filter(HistorialClinico.id_consulta == consulta_id)\
               .order_by(HistorialClinico.fecha_evento).all()

    def get_eventos_por_tratamiento(self, db: Session, *, tratamiento_id: int) -> List[HistorialClinico]:
        """Obtener eventos relacionados a un tratamiento específico"""
        return db.query(HistorialClinico)\
               .filter(HistorialClinico.id_tratamiento == tratamiento_id)\
               .order_by(HistorialClinico.fecha_evento).all()

    def get_pesos_historicos(self, db: Session, *, mascota_id: int) -> List[Dict[str, Any]]:
        """Obtener histórico de pesos de una mascota"""
        pesos = db.query(
            HistorialClinico.fecha_evento,
            HistorialClinico.peso_momento,
            HistorialClinico.edad_meses
        ).filter(
            and_(
                HistorialClinico.id_mascota == mascota_id,
                HistorialClinico.peso_momento.isnot(None)
            )
        ).order_by(HistorialClinico.fecha_evento).all()
        
        return [
            {
                "fecha": p.fecha_evento,
                "peso": float(p.peso_momento),
                "edad_meses": p.edad_meses
            }
            for p in pesos
        ]

    def add_evento_consulta(self, db: Session, *, mascota_id: int, consulta_id: int, veterinario_id: int, 
                           descripcion: str, peso_actual: float = None) -> HistorialClinico:
        """Agregar evento específico de consulta"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_consulta=consulta_id,
            id_veterinario=veterinario_id,
            tipo_evento="Consulta médica",
            descripcion_evento=descripcion,
            peso_momento=peso_actual,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def add_evento_diagnostico(self, db: Session, *, mascota_id: int, diagnostico_id: int, 
                              veterinario_id: int, descripcion: str) -> HistorialClinico:
        """Agregar evento específico de diagnóstico"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_diagnostico=diagnostico_id,
            id_veterinario=veterinario_id,
            tipo_evento="Diagnóstico",
            descripcion_evento=descripcion,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def add_evento_tratamiento(self, db: Session, *, mascota_id: int, tratamiento_id: int, 
                              veterinario_id: int, descripcion: str) -> HistorialClinico:
        """Agregar evento específico de tratamiento"""
        evento_data = HistorialClinicoCreate(
            id_mascota=mascota_id,
            id_tratamiento=tratamiento_id,
            id_veterinario=veterinario_id,
            tipo_evento="Tratamiento",
            descripcion_evento=descripcion,
            fecha_evento=datetime.now()
        )
        return self.add_evento(db, evento_data=evento_data)

    def get_resumen_mascota(self, db: Session, *, mascota_id: int) -> Dict[str, Any]:
        """Obtener resumen del historial de una mascota"""
        # Último evento
        ultimo_evento = db.query(HistorialClinico)\
                         .filter(HistorialClinico.id_mascota == mascota_id)\
                         .order_by(desc(HistorialClinico.fecha_evento)).first()
        
        # Último peso registrado
        ultimo_peso = db.query(HistorialClinico.peso_momento)\
                        .filter(
                            and_(
                                HistorialClinico.id_mascota == mascota_id,
                                HistorialClinico.peso_momento.isnot(None)
                            )
                        )\
                        .order_by(desc(HistorialClinico.fecha_evento)).first()
        
        # Conteos
        total_consultas = db.query(HistorialClinico)\
                           .filter(
                               and_(
                                   HistorialClinico.id_mascota == mascota_id,
                                   HistorialClinico.tipo_evento.ilike("%consulta%")
                               )
                           ).count()
        
        total_tratamientos = db.query(HistorialClinico)\
                            .filter(
                                and_(
                                    HistorialClinico.id_mascota == mascota_id,
                                    HistorialClinico.id_tratamiento.isnot(None)
                                )
                            ).count()
        
        return {
            "ultimo_evento": {
                "fecha": ultimo_evento.fecha_evento if ultimo_evento else None,
                "tipo": ultimo_evento.tipo_evento if ultimo_evento else None,
                "descripcion": ultimo_evento.descripcion_evento if ultimo_evento else None
            },
            "ultimo_peso": float(ultimo_peso.peso_momento) if ultimo_peso and ultimo_peso.peso_momento else None,
            "estadisticas": {
                "total_eventos": db.query(HistorialClinico).filter(HistorialClinico.id_mascota == mascota_id).count(),
                "total_consultas": total_consultas,
                "total_tratamientos": total_tratamientos
            }
        }


# Instancia única
historial_clinico = CRUDHistorialClinico(HistorialClinico)