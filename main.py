# main.py - Sistema Veterinaria API
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import os
from datetime import datetime
from app.config.database import get_db
from app.models.clientes import Cliente
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.veterinario import Veterinario
from app.models.mascota import Mascota
from app.models.tipo_servicio import TipoServicio
from app.crud.clientes_crud import cliente
from app.schemas.clientes_schema import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse

app = FastAPI(
    title="🏥 Sistema Veterinaria API",
    description="API para gestión de clientes veterinarios",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== ENDPOINTS BÁSICOS =====

@app.get("/")
async def root():
    return {
        "message": "🏥 Sistema Veterinaria API funcionando!",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "status": "OK",
        "endpoints": [
            "/health - Estado del sistema",
            "/test-db - Probar conexión DB",
            "/clientes - Lista de clientes",
            "/clientes/{id} - Cliente específico",
            "/clientes/dni/{dni} - Cliente por DNI",
            "/usuarios - Lista de usuarios",
            "/administradores - Lista de administradores",
            "/veterinarios - Lista de veterinarios",
            "/mascotas - Lista de mascotas",
            "/tipos-servicio - Lista de tipos de servicio",
            "/usuarios - Lista de usuarios",
            "/administradores - Lista de administradores",
            "/veterinarios - Lista de veterinarios",
            "/mascotas - Lista de mascotas",
            "/tipos-servicio - Lista de tipos de servicio"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "veterinaria-api"
    }


@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Probar conexión a la base de datos"""
    try:
        # Test simple
        result = db.execute("SELECT 1 as test").fetchone()

        # Test con tabla Cliente
        cliente_count = db.query(Cliente).count()

        return {
            "status": "success",
            "message": "Conexión exitosa a la base de datos",
            "test_query": "OK",
            "total_clientes": cliente_count,
            "timestamp": datetime.now().isoformat()
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )


# ===== ENDPOINTS DE USUARIOS (SOLO LECTURA) =====

@app.get("/usuarios")
async def get_usuarios(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        tipo_usuario: Optional[str] = Query(None, description="Filtrar por tipo"),
        estado: Optional[str] = Query(None, description="Filtrar por estado")
):
    """Obtener lista de usuarios"""
    try:
        skip = (page - 1) * per_page

        # Query base
        query = db.execute("SELECT * FROM usuarios")
        usuarios_raw = query.fetchall()

        # Aplicar filtros manualmente
        usuarios_filtrados = []
        for usuario in usuarios_raw:
            incluir = True
            if tipo_usuario and usuario.tipo_usuario != tipo_usuario:
                incluir = False
            if estado and usuario.estado != estado:
                incluir = False
            if incluir:
                usuarios_filtrados.append({
                    "id_usuario": usuario.id_usuario,
                    "username": usuario.username,
                    "tipo_usuario": usuario.tipo_usuario,
                    "fecha_creacion": usuario.fecha_creacion,
                    "estado": usuario.estado
                })

        total = len(usuarios_filtrados)
        usuarios_paginados = usuarios_filtrados[skip:skip + per_page]

        return {
            "usuarios": usuarios_paginados,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar usuarios: {str(e)}")


@app.get("/usuarios/{usuario_id}")
async def get_usuario_by_id(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener usuario por ID"""
    try:
        result = db.execute("SELECT * FROM usuarios WHERE id_usuario = :id", {"id": usuario_id})
        usuario = result.fetchone()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return {
            "id_usuario": usuario.id_usuario,
            "username": usuario.username,
            "tipo_usuario": usuario.tipo_usuario,
            "fecha_creacion": usuario.fecha_creacion,
            "estado": usuario.estado
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar usuario: {str(e)}")


# ===== ENDPOINTS DE ADMINISTRADORES (SOLO LECTURA) =====

@app.get("/administradores")
async def get_administradores(db: Session = Depends(get_db)):
    """Obtener lista de administradores"""
    try:
        query = db.execute("""
            SELECT a.*, u.username, u.estado as estado_usuario 
            FROM Administrador a 
            JOIN usuarios u ON a.id_usuario = u.id_usuario
        """)
        administradores = query.fetchall()

        resultado = []
        for admin in administradores:
            resultado.append({
                "id_administrador": admin.id_administrador,
                "id_usuario": admin.id_usuario,
                "username": admin.username,
                "nombre": admin.nombre,
                "apellido_paterno": admin.apellido_paterno,
                "apellido_materno": admin.apellido_materno,
                "dni": admin.dni,
                "telefono": admin.telefono,
                "email": admin.email,
                "fecha_ingreso": admin.fecha_ingreso,
                "genero": admin.genero,
                "estado_usuario": admin.estado_usuario
            })

        return {"administradores": resultado, "total": len(resultado)}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar administradores: {str(e)}")


@app.get("/administradores/{admin_id}")
async def get_administrador_by_id(admin_id: int, db: Session = Depends(get_db)):
    """Obtener administrador por ID"""
    try:
        result = db.execute("""
            SELECT a.*, u.username, u.estado as estado_usuario 
            FROM Administrador a 
            JOIN usuarios u ON a.id_usuario = u.id_usuario
            WHERE a.id_administrador = :id
        """, {"id": admin_id})
        admin = result.fetchone()

        if not admin:
            raise HTTPException(status_code=404, detail="Administrador no encontrado")

        return {
            "id_administrador": admin.id_administrador,
            "id_usuario": admin.id_usuario,
            "username": admin.username,
            "nombre": admin.nombre,
            "apellido_paterno": admin.apellido_paterno,
            "apellido_materno": admin.apellido_materno,
            "dni": admin.dni,
            "telefono": admin.telefono,
            "email": admin.email,
            "fecha_ingreso": admin.fecha_ingreso,
            "genero": admin.genero,
            "estado_usuario": admin.estado_usuario
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar administrador: {str(e)}")


# ===== ENDPOINTS DE VETERINARIOS (SOLO LECTURA) =====

@app.get("/veterinarios")
async def get_veterinarios(
        db: Session = Depends(get_db),
        especialidad_id: Optional[int] = Query(None, description="Filtrar por especialidad"),
        turno: Optional[str] = Query(None, description="Filtrar por turno"),
        disposicion: Optional[str] = Query(None, description="Filtrar por disponibilidad")
):
    """Obtener lista de veterinarios"""
    try:
        query = db.execute("""
            SELECT v.*, e.descripcion as especialidad_nombre, u.username, u.estado as estado_usuario 
            FROM Veterinario v 
            JOIN Especialidad e ON v.id_especialidad = e.id_especialidad
            JOIN usuarios u ON v.id_usuario = u.id_usuario
        """)
        veterinarios = query.fetchall()

        resultado = []
        for vet in veterinarios:
            incluir = True
            if especialidad_id and vet.id_especialidad != especialidad_id:
                incluir = False
            if turno and vet.turno != turno:
                incluir = False
            if disposicion and vet.disposicion != disposicion:
                incluir = False

            if incluir:
                resultado.append({
                    "id_veterinario": vet.id_veterinario,
                    "id_usuario": vet.id_usuario,
                    "username": vet.username,
                    "codigo_CMVP": vet.codigo_CMVP,
                    "tipo_veterinario": vet.tipo_veterinario,
                    "nombre": vet.nombre,
                    "apellido_paterno": vet.apellido_paterno,
                    "apellido_materno": vet.apellido_materno,
                    "dni": vet.dni,
                    "telefono": vet.telefono,
                    "email": vet.email,
                    "fecha_nacimiento": vet.fecha_nacimiento,
                    "genero": vet.genero,
                    "fecha_ingreso": vet.fecha_ingreso,
                    "disposicion": vet.disposicion,
                    "turno": vet.turno,
                    "especialidad_id": vet.id_especialidad,
                    "especialidad_nombre": vet.especialidad_nombre,
                    "estado_usuario": vet.estado_usuario
                })

        return {"veterinarios": resultado, "total": len(resultado)}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar veterinarios: {str(e)}")


@app.get("/veterinarios/{vet_id}")
async def get_veterinario_by_id(vet_id: int, db: Session = Depends(get_db)):
    """Obtener veterinario por ID"""
    try:
        result = db.execute("""
            SELECT v.*, e.descripcion as especialidad_nombre, u.username, u.estado as estado_usuario 
            FROM Veterinario v 
            JOIN Especialidad e ON v.id_especialidad = e.id_especialidad
            JOIN usuarios u ON v.id_usuario = u.id_usuario
            WHERE v.id_veterinario = :id
        """, {"id": vet_id})
        vet = result.fetchone()

        if not vet:
            raise HTTPException(status_code=404, detail="Veterinario no encontrado")

        return {
            "id_veterinario": vet.id_veterinario,
            "id_usuario": vet.id_usuario,
            "username": vet.username,
            "codigo_CMVP": vet.codigo_CMVP,
            "tipo_veterinario": vet.tipo_veterinario,
            "nombre": vet.nombre,
            "apellido_paterno": vet.apellido_paterno,
            "apellido_materno": vet.apellido_materno,
            "dni": vet.dni,
            "telefono": vet.telefono,
            "email": vet.email,
            "fecha_nacimiento": vet.fecha_nacimiento,
            "genero": vet.genero,
            "fecha_ingreso": vet.fecha_ingreso,
            "disposicion": vet.disposicion,
            "turno": vet.turno,
            "especialidad_id": vet.id_especialidad,
            "especialidad_nombre": vet.especialidad_nombre,
            "estado_usuario": vet.estado_usuario
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar veterinario: {str(e)}")


# ===== ENDPOINTS DE MASCOTAS (SOLO LECTURA) =====

@app.get("/mascotas")
async def get_mascotas(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        raza_id: Optional[int] = Query(None, description="Filtrar por raza"),
        sexo: Optional[str] = Query(None, description="Filtrar por sexo")
):
    """Obtener lista de mascotas"""
    try:
        skip = (page - 1) * per_page

        query = db.execute("""
            SELECT m.*, r.nombre_raza, 
                   cm.id_cliente, c.nombre as cliente_nombre, 
                   c.apellido_paterno as cliente_apellido
            FROM Mascota m 
            JOIN Raza r ON m.id_raza = r.id_raza
            LEFT JOIN Cliente_Mascota cm ON m.id_mascota = cm.id_mascota
            LEFT JOIN Cliente c ON cm.id_cliente = c.id_cliente
        """)
        mascotas = query.fetchall()

        resultado = []
        for mascota in mascotas:
            incluir = True
            if raza_id and mascota.id_raza != raza_id:
                incluir = False
            if sexo and mascota.sexo != sexo:
                incluir = False

            if incluir:
                resultado.append({
                    "id_mascota": mascota.id_mascota,
                    "nombre": mascota.nombre,
                    "sexo": mascota.sexo,
                    "color": mascota.color,
                    "edad_anios": mascota.edad_anios,
                    "edad_meses": mascota.edad_meses,
                    "esterilizado": mascota.esterilizado,
                    "imagen": mascota.imagen,
                    "raza_id": mascota.id_raza,
                    "raza_nombre": mascota.nombre_raza,
                    "cliente_id": mascota.id_cliente,
                    "cliente_nombre": f"{mascota.cliente_nombre} {mascota.cliente_apellido}" if mascota.cliente_nombre else None
                })

        total = len(resultado)
        mascotas_paginadas = resultado[skip:skip + per_page]

        return {
            "mascotas": mascotas_paginadas,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar mascotas: {str(e)}")


@app.get("/mascotas/{mascota_id}")
async def get_mascota_by_id(mascota_id: int, db: Session = Depends(get_db)):
    """Obtener mascota por ID"""
    try:
        result = db.execute("""
            SELECT m.*, r.nombre_raza, 
                   cm.id_cliente, c.nombre as cliente_nombre, 
                   c.apellido_paterno as cliente_apellido
            FROM Mascota m 
            JOIN Raza r ON m.id_raza = r.id_raza
            LEFT JOIN Cliente_Mascota cm ON m.id_mascota = cm.id_mascota
            LEFT JOIN Cliente c ON cm.id_cliente = c.id_cliente
            WHERE m.id_mascota = :id
        """, {"id": mascota_id})
        mascota = result.fetchone()

        if not mascota:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")

        return {
            "id_mascota": mascota.id_mascota,
            "nombre": mascota.nombre,
            "sexo": mascota.sexo,
            "color": mascota.color,
            "edad_anios": mascota.edad_anios,
            "edad_meses": mascota.edad_meses,
            "esterilizado": mascota.esterilizado,
            "imagen": mascota.imagen,
            "raza_id": mascota.id_raza,
            "raza_nombre": mascota.nombre_raza,
            "cliente_id": mascota.id_cliente,
            "cliente_nombre": f"{mascota.cliente_nombre} {mascota.cliente_apellido}" if mascota.cliente_nombre else None
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar mascota: {str(e)}")


# ===== ENDPOINTS DE TIPOS DE SERVICIO (SOLO LECTURA) =====

@app.get("/tipos-servicio")
async def get_tipos_servicio(db: Session = Depends(get_db)):
    """Obtener lista de tipos de servicio"""
    try:
        query = db.execute("SELECT * FROM Tipo_servicio")
        tipos = query.fetchall()

        resultado = []
        for tipo in tipos:
            resultado.append({
                "id_tipo_servicio": tipo.id_tipo_servicio,
                "descripcion": tipo.descripcion
            })

        return {"tipos_servicio": resultado, "total": len(resultado)}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar tipos de servicio: {str(e)}")


@app.get("/tipos-servicio/{tipo_id}")
async def get_tipo_servicio_by_id(tipo_id: int, db: Session = Depends(get_db)):
    """Obtener tipo de servicio por ID"""
    try:
        result = db.execute("SELECT * FROM Tipo_servicio WHERE id_tipo_servicio = :id", {"id": tipo_id})
        tipo = result.fetchone()

        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de servicio no encontrado")

        return {
            "id_tipo_servicio": tipo.id_tipo_servicio,
            "descripcion": tipo.descripcion
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar tipo de servicio: {str(e)}")


# ===== ENDPOINTS DE CLIENTES (EXISTENTES) =====

@app.get("/clientes", response_model=ClienteListResponse)
async def get_clientes(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        estado: Optional[str] = Query(None, description="Filtrar por estado (Activo/Inactivo)")
):
    """Obtener lista de clientes con paginación"""
    try:
        skip = (page - 1) * per_page

        # Construir query
        query = db.query(Cliente)

        # Filtrar por estado si se proporciona
        if estado:
            if estado not in ["Activo", "Inactivo"]:
                raise HTTPException(
                    status_code=400,
                    detail="Estado debe ser 'Activo' o 'Inactivo'"
                )
            query = query.filter(Cliente.estado == estado)

        # Contar total
        total = query.count()

        # Obtener clientes con paginación
        clientes = query.order_by(Cliente.fecha_registro.desc()) \
            .offset(skip) \
            .limit(per_page) \
            .all()

        return {
            "clientes": clientes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar clientes: {str(e)}"
        )


@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def get_cliente_by_id(
        cliente_id: int,
        db: Session = Depends(get_db)
):
    """Obtener un cliente específico por ID"""
    try:
        cliente_obj = cliente.get(db, id=cliente_id)

        if not cliente_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente con ID {cliente_id} no encontrado"
            )

        return cliente_obj

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar cliente: {str(e)}"
        )


@app.get("/clientes/dni/{dni}", response_model=ClienteResponse)
async def get_cliente_by_dni(
        dni: str,
        db: Session = Depends(get_db)
):
    """Obtener cliente por DNI"""
    try:
        # Validar formato DNI
        if len(dni) != 8 or not dni.isdigit():
            raise HTTPException(
                status_code=400,
                detail="DNI debe tener exactamente 8 dígitos"
            )

        cliente_obj = cliente.get_by_dni(db, dni=dni)

        if not cliente_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente con DNI {dni} no encontrado"
            )

        return cliente_obj

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar cliente: {str(e)}"
        )


@app.post("/clientes", response_model=ClienteResponse)
async def create_cliente(
        cliente_data: ClienteCreate,
        db: Session = Depends(get_db)
):
    """Crear un nuevo cliente"""
    try:
        # Validar duplicados
        if cliente.exists_by_dni(db, dni=cliente_data.dni):
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un cliente con DNI {cliente_data.dni}"
            )

        if cliente.exists_by_email(db, email=cliente_data.email):
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un cliente con email {cliente_data.email}"
            )

        # Crear cliente
        nuevo_cliente = cliente.create(db, obj_in=cliente_data)

        return nuevo_cliente

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear cliente: {str(e)}"
        )


@app.put("/clientes/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
        cliente_id: int,
        cliente_data: ClienteUpdate,
        db: Session = Depends(get_db)
):
    """Actualizar un cliente"""
    try:
        # Verificar que existe
        cliente_obj = cliente.get(db, id=cliente_id)
        if not cliente_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente con ID {cliente_id} no encontrado"
            )

        # Validar duplicados en campos únicos si se están actualizando
        update_data = cliente_data.dict(exclude_unset=True)

        if "email" in update_data:
            if cliente.exists_by_email(db, email=update_data["email"], exclude_id=cliente_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe un cliente con email {update_data['email']}"
                )

        # Actualizar cliente
        cliente_actualizado = cliente.update(db, db_obj=cliente_obj, obj_in=cliente_data)

        return cliente_actualizado

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar cliente: {str(e)}"
        )


@app.delete("/clientes/{cliente_id}")
async def delete_cliente(
        cliente_id: int,
        db: Session = Depends(get_db),
        permanent: bool = Query(False, description="Eliminación permanente")
):
    """Eliminar/desactivar un cliente"""
    try:
        cliente_obj = cliente.get(db, id=cliente_id)
        if not cliente_obj:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente con ID {cliente_id} no encontrado"
            )

        if permanent:
            # Eliminación permanente
            cliente.remove(db, id=cliente_id)
            message = f"Cliente {cliente_id} eliminado permanentemente"
        else:
            # Soft delete - cambiar estado a Inactivo
            cliente_obj.estado = "Inactivo"
            db.commit()
            message = f"Cliente {cliente_id} desactivado"

        return {
            "message": message,
            "success": True,
            "cliente_id": cliente_id
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar cliente: {str(e)}"
        )


# ===== ENDPOINTS DE ESTADÍSTICAS =====

@app.get("/stats")
async def get_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    try:
        total_clientes = db.query(Cliente).count()
        clientes_activos = db.query(Cliente).filter(Cliente.estado == "Activo").count()
        clientes_inactivos = db.query(Cliente).filter(Cliente.estado == "Inactivo").count()

        # Estadísticas adicionales
        stats = {
            "clientes": {
                "total": total_clientes,
                "activos": clientes_activos,
                "inactivos": clientes_inactivos,
                "porcentaje_activos": round((clientes_activos / total_clientes * 100), 2) if total_clientes > 0 else 0
            },
            "timestamp": datetime.now().isoformat()
        }

        # Estadísticas adicionales con otros módulos
        try:
            stats["usuarios"] = {
                "total": db.query(Usuario).count(),
                "activos": db.query(Usuario).filter(Usuario.estado == "Activo").count(),
                "por_tipo": {
                    "administradores": db.query(Usuario).filter(Usuario.tipo_usuario == "Administrador").count(),
                    "veterinarios": db.query(Usuario).filter(Usuario.tipo_usuario == "Veterinario").count(),
                    "recepcionistas": db.query(Usuario).filter(Usuario.tipo_usuario == "Recepcionista").count()
                }
            }

            stats["mascotas"] = {
                "total": db.query(Mascota).count(),
                "esterilizadas": db.query(Mascota).filter(Mascota.esterilizado == True).count(),
                "por_sexo": {
                    "machos": db.query(Mascota).filter(Mascota.sexo == "Macho").count(),
                    "hembras": db.query(Mascota).filter(Mascota.sexo == "Hembra").count()
                }
            }

            stats["veterinarios"] = {
                "total": db.query(Veterinario).count(),
                "disponibles": db.query(Veterinario).filter(Veterinario.disposicion == "Libre").count(),
                "ocupados": db.query(Veterinario).filter(Veterinario.disposicion == "Ocupado").count()
            }

            stats["tipos_servicio"] = db.query(TipoServicio).count()

        except SQLAlchemyError:
            # Si alguna tabla no existe, continuar sin error
            pass

        return stats

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ===== ENDPOINT DE BÚSQUEDA =====

@app.get("/clientes/search/")
async def search_clientes(
    db: Session = Depends(get_db),
    nombre: Optional[str] = Query(None, description="Buscar por nombre o apellidos"),
    dni: Optional[str] = Query(None, description="Buscar por DNI"),
    email: Optional[str] = Query(None, description="Buscar por email"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Buscar clientes con múltiples filtros"""
    try:
        query = db.query(Cliente)
        
        # Aplicar filtros
        if nombre:
            nombre_filter = f"%{nombre}%"
            query = query.filter(
                Cliente.nombre.ilike(nombre_filter) |
                Cliente.apellido_paterno.ilike(nombre_filter) |
                Cliente.apellido_materno.ilike(nombre_filter)
            )
        
        if dni:
            query = query.filter(Cliente.dni == dni)
        
        if email:
            query = query.filter(Cliente.email.ilike(f"%{email}%"))
        
        if estado:
            query = query.filter(Cliente.estado == estado)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación
        skip = (page - 1) * per_page
        clientes = query.order_by(Cliente.fecha_registro.desc())\
                       .offset(skip)\
                       .limit(per_page)\
                       .all()
        
        return {
            "clientes": clientes,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "filtros_aplicados": {
                "nombre": nombre,
                "dni": dni,
                "email": email,
                "estado": estado
            }
        }
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)