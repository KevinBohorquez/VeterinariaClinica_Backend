# app/crud/catalogo_crud.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud.base_crud import CRUDBase
from app.models.raza import Raza
from app.models.tipo_animal import TipoAnimal
from app.models.especialidad import Especialidad
from app.models.tipo_servicio import TipoServicio
from app.models.servicio import Servicio
from app.models.patologia import Patologia
from app.schemas.catalogo_schemas import (
    RazaCreate, TipoAnimalCreate, EspecialidadCreate,
    TipoServicioCreate, ServicioCreate, ServicioUpdate, PatologiaCreate
)

# ===== RAZA =====
class CRUDRaza(CRUDBase[Raza, RazaCreate, None]):
    
    def get_by_nombre(self, db: Session, *, nombre_raza: str) -> Optional[Raza]:
        """Obtener raza por nombre"""
        return db.query(Raza).filter(Raza.nombre_raza.ilike(f"%{nombre_raza}%")).first()

    def search_razas(self, db: Session, *, nombre: str) -> List[Raza]:
        """Buscar razas por nombre"""
        return db.query(Raza).filter(Raza.nombre_raza.ilike(f"%{nombre}%")).all()

# ===== TIPO ANIMAL =====
class CRUDTipoAnimal(CRUDBase[TipoAnimal, TipoAnimalCreate, None]):
    
    def get_by_raza(self, db: Session, *, raza_id: int) -> List[TipoAnimal]:
        """Obtener tipos de animal por raza"""
        return db.query(TipoAnimal).filter(TipoAnimal.id_raza == raza_id).all()

    def get_by_descripcion(self, db: Session, *, descripcion: str) -> List[TipoAnimal]:
        """Obtener tipos de animal por descripción (Perro/Gato)"""
        return db.query(TipoAnimal).filter(TipoAnimal.descripcion == descripcion).all()

# ===== ESPECIALIDAD =====
class CRUDEspecialidad(CRUDBase[Especialidad, EspecialidadCreate, None]):
    
    def get_by_descripcion(self, db: Session, *, descripcion: str) -> Optional[Especialidad]:
        """Obtener especialidad por descripción"""
        return db.query(Especialidad).filter(Especialidad.descripcion.ilike(f"%{descripcion}%")).first()

    def search_especialidades(self, db: Session, *, descripcion: str) -> List[Especialidad]:
        """Buscar especialidades por descripción"""
        return db.query(Especialidad).filter(Especialidad.descripcion.ilike(f"%{descripcion}%")).all()

# ===== TIPO SERVICIO =====
class CRUDTipoServicio(CRUDBase[TipoServicio, TipoServicioCreate, None]):
    
    def get_by_descripcion(self, db: Session, *, descripcion: str) -> Optional[TipoServicio]:
        """Obtener tipo de servicio por descripción"""
        return db.query(TipoServicio).filter(TipoServicio.descripcion.ilike(f"%{descripcion}%")).first()

# ===== SERVICIO =====
class CRUDServicio(CRUDBase[Servicio, ServicioCreate, ServicioUpdate]):
    
    def get_by_tipo(self, db: Session, *, tipo_servicio_id: int) -> List[Servicio]:
        """Obtener servicios por tipo"""
        return db.query(Servicio).filter(Servicio.id_tipo_servicio == tipo_servicio_id).all()

    def get_activos(self, db: Session) -> List[Servicio]:
        """Obtener servicios activos"""
        return db.query(Servicio).filter(Servicio.activo == True).all()

    def get_by_nombre(self, db: Session, *, nombre_servicio: str) -> Optional[Servicio]:
        """Obtener servicio por nombre"""
        return db.query(Servicio).filter(Servicio.nombre_servicio.ilike(f"%{nombre_servicio}%")).first()

    def search_servicios(self, db: Session, *, nombre: str = None, activo: bool = None) -> List[Servicio]:
        """Buscar servicios"""
        query = db.query(Servicio)
        
        if nombre:
            query = query.filter(Servicio.nombre_servicio.ilike(f"%{nombre}%"))
        
        if activo is not None:
            query = query.filter(Servicio.activo == activo)
        
        return query.all()

    def get_by_precio_range(self, db: Session, *, precio_min: float = None, precio_max: float = None) -> List[Servicio]:
        """Obtener servicios por rango de precio"""
        query = db.query(Servicio)
        
        if precio_min is not None:
            query = query.filter(Servicio.precio >= precio_min)
        
        if precio_max is not None:
            query = query.filter(Servicio.precio <= precio_max)
        
        return query.all()

# ===== PATOLOGÍA =====
class CRUDPatologia(CRUDBase[Patologia, PatologiaCreate, None]):
    
    def get_by_nombre(self, db: Session, *, nombre_patologia: str) -> Optional[Patologia]:
        """Obtener patología por nombre"""
        return db.query(Patologia).filter(Patologia.nombre_patologia.ilike(f"%{nombre_patologia}%")).first()

    def get_by_especie(self, db: Session, *, especie: str) -> List[Patologia]:
        """Obtener patologías por especie"""
        return db.query(Patologia).filter(
            (Patologia.especie_afecta == especie) | (Patologia.especie_afecta == "Ambas")
        ).all()

    def get_by_gravedad(self, db: Session, *, gravedad: str) -> List[Patologia]:
        """Obtener patologías por gravedad"""
        return db.query(Patologia).filter(Patologia.gravedad == gravedad).all()

    def get_cronicas(self, db: Session) -> List[Patologia]:
        """Obtener patologías crónicas"""
        return db.query(Patologia).filter(Patologia.es_crónica == True).all()

    def get_contagiosas(self, db: Session) -> List[Patologia]:
        """Obtener patologías contagiosas"""
        return db.query(Patologia).filter(Patologia.es_contagiosa == True).all()

    def search_patologias(self, db: Session, *, nombre: str = None, especie: str = None, gravedad: str = None) -> List[Patologia]:
        """Buscar patologías con múltiples filtros"""
        query = db.query(Patologia)
        
        if nombre:
            query = query.filter(Patologia.nombre_patologia.ilike(f"%{nombre}%"))
        
        if especie:
            query = query.filter(
                (Patologia.especie_afecta == especie) | (Patologia.especie_afecta == "Ambas")
            )
        
        if gravedad:
            query = query.filter(Patologia.gravedad == gravedad)
        
        return query.all()

# Instancias únicas
raza = CRUDRaza(Raza)
tipo_animal = CRUDTipoAnimal(TipoAnimal)
especialidad = CRUDEspecialidad(Especialidad)
tipo_servicio = CRUDTipoServicio(TipoServicio)
servicio = CRUDServicio(Servicio)
patologia = CRUDPatologia(Patologia)