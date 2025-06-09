# app/crud/mascota_crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from app.crud.base_crud import CRUDBase
from app.models.mascota import Mascota
from app.models.clientes import Cliente
from app.models.raza import Raza
from app.schemas.mascota_schema import MascotaCreate, MascotaUpdate, MascotaSearch

class CRUDMascota(CRUDBase[Mascota, MascotaCreate, MascotaUpdate]):
    
    def get_mascotas_by_cliente(self, db: Session, *, cliente_id: int) -> List[Mascota]:
        """Obtener todas las mascotas de un cliente"""
        return db.query(Mascota).filter(Mascota.id_cliente == cliente_id).all()

    def get_mascotas_by_raza(self, db: Session, *, raza_id: int) -> List[Mascota]:
        """Obtener todas las mascotas de una raza específica"""
        return db.query(Mascota).filter(Mascota.id_raza == raza_id).all()

    def get_with_details(self, db: Session, *, mascota_id: int) -> Optional[dict]:
        """Obtener mascota con detalles del cliente y raza"""
        result = db.query(
            Mascota,
            Cliente.nombre.label('cliente_nombre'),
            Cliente.apellido_paterno.label('cliente_apellido'),
            Raza.nombre_raza.label('raza_nombre')
        ).join(Cliente, Mascota.id_cliente == Cliente.id_cliente)\
         .join(Raza, Mascota.id_raza == Raza.id_raza)\
         .filter(Mascota.id_mascota == mascota_id).first()
        
        if result:
            return {
                "mascota": result.Mascota,
                "cliente_nombre_completo": f"{result.cliente_nombre} {result.cliente_apellido}",
                "raza_nombre": result.raza_nombre
            }
        return None

    def search_mascotas(self, db: Session, *, search_params: MascotaSearch) -> Tuple[List[Mascota], int]:
        """Buscar mascotas con filtros múltiples"""
        query = db.query(Mascota)
        
        # Aplicar filtros
        if search_params.nombre:
            query = query.filter(Mascota.nombre.ilike(f"%{search_params.nombre}%"))
        
        if search_params.id_cliente:
            query = query.filter(Mascota.id_cliente == search_params.id_cliente)
        
        if search_params.id_raza:
            query = query.filter(Mascota.id_raza == search_params.id_raza)
        
        if search_params.sexo:
            query = query.filter(Mascota.sexo == search_params.sexo)
        
        if search_params.esterilizado is not None:
            query = query.filter(Mascota.esterilizado == search_params.esterilizado)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        mascotas = query.offset((search_params.page - 1) * search_params.per_page)\
                       .limit(search_params.per_page).all()
        
        return mascotas, total

    def get_mascotas_por_edad(self, db: Session, *, min_edad: int = None, max_edad: int = None) -> List[Mascota]:
        """Obtener mascotas por rango de edad"""
        query = db.query(Mascota)
        
        if min_edad is not None:
            query = query.filter(Mascota.edad_anios >= min_edad)
        
        if max_edad is not None:
            query = query.filter(Mascota.edad_anios <= max_edad)
        
        return query.all()

    def get_mascotas_no_esterilizadas(self, db: Session) -> List[Mascota]:
        """Obtener mascotas no esterilizadas"""
        return db.query(Mascota).filter(Mascota.esterilizado == False).all()

    def count_mascotas_by_sexo(self, db: Session) -> dict:
        """Contar mascotas por sexo"""
        return {
            "machos": db.query(Mascota).filter(Mascota.sexo == "Macho").count(),
            "hembras": db.query(Mascota).filter(Mascota.sexo == "Hembra").count()
        }

    def get_mascotas_with_cliente_info(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[dict]:
        """Obtener mascotas con información del cliente"""
        results = db.query(
            Mascota,
            Cliente.nombre.label('cliente_nombre'),
            Cliente.telefono.label('cliente_telefono'),
            Cliente.email.label('cliente_email')
        ).join(Cliente, Mascota.id_cliente == Cliente.id_cliente)\
         .offset(skip).limit(limit).all()
        
        return [
            {
                "mascota": result.Mascota,
                "cliente_nombre": result.cliente_nombre,
                "cliente_telefono": result.cliente_telefono,
                "cliente_email": result.cliente_email
            }
            for result in results
        ]

# Instancia única
mascota = CRUDMascota(Mascota)