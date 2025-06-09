# app/crud/mascota.py (SIMPLE Y FUNCIONAL)
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.schemas.mascota_schema import MascotaCreate, MascotaUpdate


def get(db: Session, mascota_id: int) -> Optional[Mascota]:
    """Obtener mascota por ID"""
    return db.query(Mascota).filter(Mascota.id_mascota == mascota_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Mascota]:
    """Obtener todas las mascotas"""
    return db.query(Mascota).offset(skip).limit(limit).all()


def create(db: Session, obj_in: MascotaCreate) -> Mascota:
    """Crear nueva mascota"""
    mascota_data = obj_in.dict()

    db_obj = Mascota(**mascota_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return db_obj


def update(db: Session, db_obj: Mascota, obj_in: MascotaUpdate) -> Mascota:
    """Actualizar mascota"""
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: int) -> Optional[Mascota]:
    """Eliminar mascota permanentemente"""
    # Primero eliminar todas las relaciones cliente-mascota
    db.query(ClienteMascota).filter(ClienteMascota.id_mascota == id).delete()

    # Luego eliminar la mascota
    obj = db.query(Mascota).filter(Mascota.id_mascota == id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj


def get_mascotas_by_cliente(db: Session, cliente_id: int) -> List[Dict]:
    """Obtener mascotas de un cliente específico usando la tabla intermedia"""
    query = text("""
        SELECT 
            m.id_mascota,
            m.nombre,
            m.sexo,
            m.color,
            m.edad_anios,
            m.edad_meses,
            m.esterilizado,
            m.imagen,
            m.id_raza,
            r.nombre_raza,
            r.especie
        FROM Mascota m
        INNER JOIN Cliente_Mascota cm ON m.id_mascota = cm.id_mascota
        LEFT JOIN Raza r ON m.id_raza = r.id_raza
        WHERE cm.id_cliente = :cliente_id
    """)

    result = db.execute(query, {"cliente_id": cliente_id}).fetchall()

    mascotas = []
    for row in result:
        mascotas.append({
            "id_mascota": row.id_mascota,
            "nombre": row.nombre,
            "sexo": row.sexo,
            "color": row.color,
            "edad_anios": row.edad_anios,
            "edad_meses": row.edad_meses,
            "esterilizado": bool(row.esterilizado) if row.esterilizado is not None else False,
            "imagen": row.imagen,
            "id_raza": row.id_raza,
            "raza": {
                "nombre_raza": row.nombre_raza,
                "especie": row.especie
            } if row.nombre_raza else None
        })

    return mascotas


def count_mascotas_by_sexo(db: Session) -> Dict[str, int]:
    """Contar mascotas por sexo"""
    machos = db.query(Mascota).filter(Mascota.sexo == "Macho").count()
    hembras = db.query(Mascota).filter(Mascota.sexo == "Hembra").count()

    return {
        "machos": machos,
        "hembras": hembras
    }


def get_mascotas_no_esterilizadas(db: Session) -> List[Dict]:
    """Obtener mascotas no esterilizadas"""
    mascotas = db.query(Mascota).filter(Mascota.esterilizado == False).all()

    result = []
    for mascota in mascotas:
        result.append({
            "id_mascota": mascota.id_mascota,
            "nombre": mascota.nombre,
            "sexo": mascota.sexo,
            "edad_anios": mascota.edad_anios,
            "edad_meses": mascota.edad_meses,
            "esterilizado": mascota.esterilizado
        })

    return result


def search_mascotas(db: Session, search_params) -> tuple:
    """Buscar mascotas con filtros"""
    query = db.query(Mascota)

    # Aplicar filtros si existen
    if hasattr(search_params, 'nombre') and search_params.nombre:
        query = query.filter(Mascota.nombre.ilike(f"%{search_params.nombre}%"))

    if hasattr(search_params, 'sexo') and search_params.sexo:
        query = query.filter(Mascota.sexo == search_params.sexo)

    if hasattr(search_params, 'id_raza') and search_params.id_raza:
        query = query.filter(Mascota.id_raza == search_params.id_raza)

    if hasattr(search_params, 'esterilizado') and search_params.esterilizado is not None:
        query = query.filter(Mascota.esterilizado == search_params.esterilizado)

    total = query.count()

    # Paginación
    if hasattr(search_params, 'page') and hasattr(search_params, 'per_page'):
        skip = (search_params.page - 1) * search_params.per_page
        query = query.offset(skip).limit(search_params.per_page)

    mascotas = query.all()

    return mascotas, total


def asociar_cliente(db: Session, mascota_id: int, cliente_id: int) -> bool:
    """Asociar una mascota a un cliente"""
    # Verificar que no existe ya la relación
    existing = db.query(ClienteMascota).filter(
        ClienteMascota.id_mascota == mascota_id,
        ClienteMascota.id_cliente == cliente_id
    ).first()

    if existing:
        return False

    # Crear la relación
    relacion = ClienteMascota(
        id_cliente=cliente_id,
        id_mascota=mascota_id
    )
    db.add(relacion)
    db.commit()

    return True


def desasociar_cliente(db: Session, mascota_id: int, cliente_id: int) -> bool:
    """Desasociar una mascota de un cliente"""
    relacion = db.query(ClienteMascota).filter(
        ClienteMascota.id_mascota == mascota_id,
        ClienteMascota.id_cliente == cliente_id
    ).first()

    if not relacion:
        return False

    db.delete(relacion)
    db.commit()

    return True