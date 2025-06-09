# main.py - Sistema Veterinaria API (Solo Lectura)
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import os
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.config.database import get_db
from app.models.clientes import Cliente
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.veterinario import Veterinario
from app.models.mascota import Mascota
from app.models.tipo_servicio import TipoServicio
from app.models.especialidad import Especialidad
from app.models.raza import Raza
from app.models.cliente_mascota import ClienteMascota

app = FastAPI(
    title="🏥 Sistema Veterinaria API",
    description="API para consulta de datos veterinarios",
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
    base_url = os.getenv("BASE_URL", "https://backendveterinariabd.up.railway.app")  # Cambia por tu dominio real

    return {
        "message": "🏥 Sistema Veterinaria API funcionando!",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "status": "OK",
        "navigation": {
            "📊 Sistema": {
                "health": f"{base_url}/health",
                "test_db": f"{base_url}/test-db",
                "estadisticas": f"{base_url}/stats"
            },
            "👥 Usuarios": {
                "lista": f"{base_url}/usuarios",
                "ejemplo_por_id": f"{base_url}/usuarios/1"
            },
            "👨‍💼 Administradores": {
                "lista": f"{base_url}/administradores",
                "ejemplo_por_id": f"{base_url}/administradores/1"
            },
            "👨‍⚕️ Veterinarios": {
                "lista": f"{base_url}/veterinarios",
                "ejemplo_por_id": f"{base_url}/veterinarios/1",
                "filtros": {
                    "por_turno_mañana": f"{base_url}/veterinarios?turno=Mañana",
                    "disponibles": f"{base_url}/veterinarios?disposicion=Libre"
                }
            },
            "👥 Clientes": {
                "lista": f"{base_url}/clientes",
                "ejemplo_por_id": f"{base_url}/clientes/1",
                "buscar": f"{base_url}/clientes/search?nombre=María",
                "filtros": {
                    "activos": f"{base_url}/clientes?estado=Activo",
                    "pagina_2": f"{base_url}/clientes?page=2"
                }
            },
            "🐕 Mascotas": {
                "lista": f"{base_url}/mascotas",
                "ejemplo_por_id": f"{base_url}/mascotas/1",
                "filtros": {
                    "machos": f"{base_url}/mascotas?sexo=Macho",
                    "por_raza": f"{base_url}/mascotas?raza_id=1"
                }
            },
            "🏥 Tipos de Servicio": {
                "lista": f"{base_url}/tipos-servicio",
                "ejemplo_por_id": f"{base_url}/tipos-servicio/1"
            }
        },
        "endpoints_raw": [
            "/health - Estado del sistema",
            "/test-db - Probar conexión DB",
            "/clientes - Lista de clientes",
            "/clientes/{id} - Cliente específico",
            "/clientes/search - Buscar clientes",
            "/usuarios - Lista de usuarios",
            "/administradores - Lista de administradores",
            "/veterinarios - Lista de veterinarios",
            "/mascotas - Lista de mascotas",
            "/tipos-servicio - Lista de tipos de servicio",
            "/stats - Estadísticas"
        ]
    }


@app.get("/form-cliente", response_class=HTMLResponse)
async def form_cliente():
    """Formulario para crear cliente"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agregar Cliente</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
            input, select { width: 100%; padding: 10px; margin: 5px 0 15px 0; box-sizing: border-box; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; cursor: pointer; border-radius: 5px; }
            .success { color: green; margin: 10px 0; }
            .error { color: red; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h2>🏥 Agregar Nuevo Cliente</h2>

        <div id="message"></div>

        <form id="clienteForm">
            <label>Nombre:</label>
            <input type="text" name="nombre" required>

            <label>Apellido Paterno:</label>
            <input type="text" name="apellido_paterno" required>

            <label>Apellido Materno:</label>
            <input type="text" name="apellido_materno" required>

            <label>DNI (8 dígitos):</label>
            <input type="text" name="dni" pattern="[0-9]{8}" maxlength="8" required>

            <label>Teléfono (9 dígitos, empieza con 9):</label>
            <input type="text" name="telefono" pattern="9[0-9]{8}" maxlength="9" required>

            <label>Email:</label>
            <input type="email" name="email" required>

            <label>Dirección:</label>
            <input type="text" name="direccion">

            <label>Género:</label>
            <select name="genero">
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
            </select>

            <button type="submit">✅ Agregar Cliente</button>
        </form>

        <script>
            document.getElementById('clienteForm').onsubmit = async function(e) {
                e.preventDefault();

                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = 'Guardando...';

                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);

                try {
                    // Construir URL para GET con parámetros
                    const params = new URLSearchParams(data);
                    const response = await fetch('/crear-cliente?' + params.toString(), {
                        method: 'GET'
                    });

                    const result = await response.json();

                    if (response.ok) {
                        messageDiv.innerHTML = '<div class="success">✅ Cliente creado exitosamente!</div>';
                        e.target.reset();
                    } else {
                        messageDiv.innerHTML = '<div class="error">❌ Error: ' + result.detail + '</div>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="error">❌ Error de conexión</div>';
                }
            };
        </script>
    </body>
    </html>
    """
    return html_content


# Endpoint GET para crear cliente (desde el formulario)
@app.get("/crear-cliente")
async def crear_cliente_get(
        nombre: str,
        apellido_paterno: str,
        apellido_materno: str,
        dni: str,
        telefono: str,
        email: str,
        direccion: str = "",
        genero: str = "M",
        db: Session = Depends(get_db)
):
    """Crear cliente via GET desde formulario"""
    try:
        # Validar DNI único
        existing = db.query(Cliente).filter(Cliente.dni == dni).first()
        if existing:
            raise HTTPException(status_code=400, detail="DNI ya existe")

        # Crear cliente
        nuevo_cliente = Cliente(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            dni=dni,
            telefono=telefono,
            email=email,
            direccion=direccion if direccion else None,
            genero=genero,
            estado="Activo"
        )

        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)

        return {
            "success": True,
            "message": "Cliente creado exitosamente",
            "cliente_id": nuevo_cliente.id_cliente
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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
        counts = {
            "usuarios": db.query(Usuario).count(),
            "clientes": db.query(Cliente).count(),
            "mascotas": db.query(Mascota).count(),
            "administradores": db.query(Administrador).count(),
            "veterinarios": db.query(Veterinario).count(),
            "tipos_servicio": db.query(TipoServicio).count()
        }

        return {
            "status": "success",
            "message": "Conexión exitosa a la base de datos",
            "counts": counts,
            "timestamp": datetime.now().isoformat()
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")


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
        query = db.query(Usuario)

        if tipo_usuario:
            query = query.filter(Usuario.tipo_usuario == tipo_usuario)
        if estado:
            query = query.filter(Usuario.estado == estado)

        total = query.count()
        usuarios = query.order_by(Usuario.fecha_creacion.desc()).offset(skip).limit(per_page).all()

        resultado = []
        for usuario in usuarios:
            resultado.append({
                "id_usuario": usuario.id_usuario,
                "username": usuario.username,
                "tipo_usuario": usuario.tipo_usuario,
                "fecha_creacion": usuario.fecha_creacion,
                "estado": usuario.estado
            })

        return {
            "usuarios": resultado,
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
        usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
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
        administradores = db.query(Administrador).all()

        resultado = []
        for admin in administradores:
            # Obtener info del usuario asociado
            usuario = db.query(Usuario).filter(Usuario.id_usuario == admin.id_usuario).first()

            resultado.append({
                "id_administrador": admin.id_administrador,
                "id_usuario": admin.id_usuario,
                "username": usuario.username if usuario else None,
                "nombre": admin.nombre,
                "apellido_paterno": admin.apellido_paterno,
                "apellido_materno": admin.apellido_materno,
                "dni": admin.dni,
                "telefono": admin.telefono,
                "email": admin.email,
                "fecha_ingreso": admin.fecha_ingreso,
                "genero": admin.genero,
                "estado_usuario": usuario.estado if usuario else None
            })

        return {"administradores": resultado, "total": len(resultado)}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar administradores: {str(e)}")


@app.get("/administradores/{admin_id}")
async def get_administrador_by_id(admin_id: int, db: Session = Depends(get_db)):
    """Obtener administrador por ID"""
    try:
        admin = db.query(Administrador).filter(Administrador.id_administrador == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Administrador no encontrado")

        # Obtener usuario asociado
        usuario = db.query(Usuario).filter(Usuario.id_usuario == admin.id_usuario).first()

        return {
            "id_administrador": admin.id_administrador,
            "id_usuario": admin.id_usuario,
            "username": usuario.username if usuario else None,
            "nombre": admin.nombre,
            "apellido_paterno": admin.apellido_paterno,
            "apellido_materno": admin.apellido_materno,
            "dni": admin.dni,
            "telefono": admin.telefono,
            "email": admin.email,
            "fecha_ingreso": admin.fecha_ingreso,
            "genero": admin.genero,
            "estado_usuario": usuario.estado if usuario else None
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
        query = db.query(Veterinario)

        if especialidad_id:
            query = query.filter(Veterinario.id_especialidad == especialidad_id)
        if turno:
            query = query.filter(Veterinario.turno == turno)
        if disposicion:
            query = query.filter(Veterinario.disposicion == disposicion)

        veterinarios = query.all()

        resultado = []
        for vet in veterinarios:
            # Obtener usuario y especialidad asociados
            usuario = db.query(Usuario).filter(Usuario.id_usuario == vet.id_usuario).first()
            especialidad = db.query(Especialidad).filter(Especialidad.id_especialidad == vet.id_especialidad).first()

            resultado.append({
                "id_veterinario": vet.id_veterinario,
                "id_usuario": vet.id_usuario,
                "username": usuario.username if usuario else None,
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
                "especialidad_nombre": especialidad.descripcion if especialidad else None,
                "estado_usuario": usuario.estado if usuario else None
            })

        return {"veterinarios": resultado, "total": len(resultado)}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar veterinarios: {str(e)}")


@app.get("/veterinarios/{vet_id}")
async def get_veterinario_by_id(vet_id: int, db: Session = Depends(get_db)):
    """Obtener veterinario por ID"""
    try:
        vet = db.query(Veterinario).filter(Veterinario.id_veterinario == vet_id).first()
        if not vet:
            raise HTTPException(status_code=404, detail="Veterinario no encontrado")

        # Obtener usuario y especialidad asociados
        usuario = db.query(Usuario).filter(Usuario.id_usuario == vet.id_usuario).first()
        especialidad = db.query(Especialidad).filter(Especialidad.id_especialidad == vet.id_especialidad).first()

        return {
            "id_veterinario": vet.id_veterinario,
            "id_usuario": vet.id_usuario,
            "username": usuario.username if usuario else None,
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
            "especialidad_nombre": especialidad.descripcion if especialidad else None,
            "estado_usuario": usuario.estado if usuario else None
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
        query = db.query(Mascota)

        if raza_id:
            query = query.filter(Mascota.id_raza == raza_id)
        if sexo:
            query = query.filter(Mascota.sexo == sexo)

        total = query.count()
        mascotas = query.offset(skip).limit(per_page).all()

        resultado = []
        for mascota in mascotas:
            # Obtener raza y cliente
            raza = db.query(Raza).filter(Raza.id_raza == mascota.id_raza).first()

            # Buscar relación cliente-mascota
            cliente_mascota = db.query(ClienteMascota).filter(ClienteMascota.id_mascota == mascota.id_mascota).first()
            cliente_info = None
            if cliente_mascota:
                cliente_obj = db.query(Cliente).filter(Cliente.id_cliente == cliente_mascota.id_cliente).first()
                if cliente_obj:
                    cliente_info = f"{cliente_obj.nombre} {cliente_obj.apellido_paterno}"

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
                "raza_nombre": raza.nombre_raza if raza else None,
                "cliente_nombre": cliente_info
            })

        return {
            "mascotas": resultado,
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
        mascota = db.query(Mascota).filter(Mascota.id_mascota == mascota_id).first()
        if not mascota:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")

        # Obtener raza y cliente
        raza = db.query(Raza).filter(Raza.id_raza == mascota.id_raza).first()

        # Buscar relación cliente-mascota
        cliente_mascota = db.query(ClienteMascota).filter(ClienteMascota.id_mascota == mascota.id_mascota).first()
        cliente_info = None
        if cliente_mascota:
            cliente_obj = db.query(Cliente).filter(Cliente.id_cliente == cliente_mascota.id_cliente).first()
            if cliente_obj:
                cliente_info = f"{cliente_obj.nombre} {cliente_obj.apellido_paterno}"

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
            "raza_nombre": raza.nombre_raza if raza else None,
            "cliente_nombre": cliente_info
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
        tipos = db.query(TipoServicio).all()

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
        tipo = db.query(TipoServicio).filter(TipoServicio.id_tipo_servicio == tipo_id).first()
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


# ===== ENDPOINTS DE CLIENTES (SOLO LECTURA) =====

@app.get("/clientes")
async def get_clientes(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Número de página"),
        per_page: int = Query(20, ge=1, le=100, description="Elementos por página"),
        estado: Optional[str] = Query(None, description="Filtrar por estado (Activo/Inactivo)")
):
    """Obtener lista de clientes con paginación"""
    try:
        skip = (page - 1) * per_page
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
        clientes = query.order_by(Cliente.fecha_registro.desc()).offset(skip).limit(per_page).all()

        resultado = []
        for cliente in clientes:
            resultado.append({
                "id_cliente": cliente.id_cliente,
                "nombre": cliente.nombre,
                "apellido_paterno": cliente.apellido_paterno,
                "apellido_materno": cliente.apellido_materno,
                "dni": cliente.dni,
                "telefono": cliente.telefono,
                "email": cliente.email,
                "direccion": cliente.direccion,
                "fecha_registro": cliente.fecha_registro,
                "estado": cliente.estado
            })

        return {
            "clientes": resultado,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar clientes: {str(e)}")


@app.get("/clientes/{cliente_id}")
async def get_cliente_by_id(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente específico por ID"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail=f"Cliente con ID {cliente_id} no encontrado")

        return {
            "id_cliente": cliente.id_cliente,
            "nombre": cliente.nombre,
            "apellido_paterno": cliente.apellido_paterno,
            "apellido_materno": cliente.apellido_materno,
            "dni": cliente.dni,
            "telefono": cliente.telefono,
            "email": cliente.email,
            "direccion": cliente.direccion,
            "fecha_registro": cliente.fecha_registro,
            "estado": cliente.estado
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar cliente: {str(e)}")


# ===== ENDPOINT DE BÚSQUEDA DE CLIENTES =====

@app.get("/clientes/search")
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
            query = query.filter(Cliente.dni.like(f"%{dni}%"))

        if email:
            query = query.filter(Cliente.email.ilike(f"%{email}%"))

        if estado:
            query = query.filter(Cliente.estado == estado)

        # Contar total
        total = query.count()

        # Aplicar paginación
        skip = (page - 1) * per_page
        clientes = query.order_by(Cliente.fecha_registro.desc()).offset(skip).limit(per_page).all()

        resultado = []
        for cliente in clientes:
            resultado.append({
                "id_cliente": cliente.id_cliente,
                "nombre": cliente.nombre,
                "apellido_paterno": cliente.apellido_paterno,
                "apellido_materno": cliente.apellido_materno,
                "dni": cliente.dni,
                "telefono": cliente.telefono,
                "email": cliente.email,
                "direccion": cliente.direccion,
                "fecha_registro": cliente.fecha_registro,
                "estado": cliente.estado
            })

        return {
            "clientes": resultado,
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
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


# ===== ENDPOINTS DE ESTADÍSTICAS =====

@app.get("/stats")
async def get_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    try:
        stats = {
            "timestamp": datetime.now().isoformat()
        }

        # Estadísticas de clientes
        try:
            total_clientes = db.query(Cliente).count()
            clientes_activos = db.query(Cliente).filter(Cliente.estado == "Activo").count()
            stats["clientes"] = {
                "total": total_clientes,
                "activos": clientes_activos,
                "inactivos": total_clientes - clientes_activos,
                "porcentaje_activos": round((clientes_activos / total_clientes * 100), 2) if total_clientes > 0 else 0
            }
        except:
            stats["clientes"] = {"error": "No se pudo obtener estadísticas de clientes"}

        # Estadísticas de usuarios
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
        except:
            stats["usuarios"] = {"error": "No se pudo obtener estadísticas de usuarios"}

        # Estadísticas de mascotas
        try:
            stats["mascotas"] = {
                "total": db.query(Mascota).count(),
                "esterilizadas": db.query(Mascota).filter(Mascota.esterilizado == True).count(),
                "por_sexo": {
                    "machos": db.query(Mascota).filter(Mascota.sexo == "Macho").count(),
                    "hembras": db.query(Mascota).filter(Mascota.sexo == "Hembra").count()
                }
            }
        except:
            stats["mascotas"] = {"error": "No se pudo obtener estadísticas de mascotas"}

        # Estadísticas de veterinarios
        try:
            stats["veterinarios"] = {
                "total": db.query(Veterinario).count(),
                "disponibles": db.query(Veterinario).filter(Veterinario.disposicion == "Libre").count(),
                "ocupados": db.query(Veterinario).filter(Veterinario.disposicion == "Ocupado").count()
            }
        except:
            stats["veterinarios"] = {"error": "No se pudo obtener estadísticas de veterinarios"}

        # Otros conteos
        try:
            stats["tipos_servicio"] = db.query(TipoServicio).count()
        except:
            stats["tipos_servicio"] = 0

        return stats

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)