# main.py (IMPORTACIONES CORREGIDAS)
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, date

# Importar configuración
from app.config.database import get_db

# Importar MODELOS SQLAlchemy (para queries)
from app.models.veterinaria import (
    Cliente as ClienteModel,
    Mascota as MascotaModel,
    Veterinario as VeterinarioModel,
    Raza as RazaModel,
    Especialidad as EspecialidadModel,
    Servicio as ServicioModel,
    TipoServicio as TipoServicioModel,
    Consulta as ConsultaModel,
    Cita as CitaModel,
    TipoAnimal as TipoAnimalModel
)

# Importar ESQUEMAS Pydantic (para responses)
from app.schemas.veterinaria import (
    Cliente, ClienteCreate, ClienteConMascotas,
    Mascota, MascotaCreate, MascotaConCliente,
    Veterinario, VeterinarioConEspecialidad,
    Raza, Especialidad, Servicio, ServicioConTipo,
    TipoServicio, Consulta, ConsultaCompleta,
    Cita, CitaCompleta,
    EstadisticasVeterinaria, EstadoEnum, SexoMascotaEnum,
    TurnoEnum, DisposicionEnum, CondicionGeneralEnum
)

app = FastAPI(
    title="🏥 Sistema Veterinaria API",
    version="1.0.0",
    description="API completa para gestión de clínica veterinaria",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================
# ENDPOINTS PRINCIPALES
# ================================

@app.get("/")
async def root():
    return {
        "message": "🏥 Sistema Veterinaria API funcionando!",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "database": "MySQL Railway",
        "features": [
            "Gestión de clientes y mascotas",
            "Sistema de citas y consultas",
            "Triaje y diagnósticos",
            "Historial clínico completo",
            "Gestión de veterinarios",
            "Servicios y tratamientos"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "veterinaria-api",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/test-db")
async def test_database(db: Session = Depends(get_db)):
    """Probar conexión a la base de datos"""
    try:
        # Intentar hacer queries a las tablas principales
        total_clientes = db.query(Cliente).count()
        total_mascotas = db.query(Mascota).count()
        total_veterinarios = db.query(Veterinario).count()

        return {
            "status": "success",
            "message": "Conexión a base de datos exitosa",
            "sample_data": {
                "total_clientes": total_clientes,
                "total_mascotas": total_mascotas,
                "total_veterinarios": total_veterinarios
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")


# ================================
# ENDPOINTS DE CLIENTES
# ================================

# EJEMPLO CORREGIDO - Endpoint de clientes
@app.get("/clientes", response_model=List[Cliente])
async def get_clientes(
        skip: int = 0,
        limit: int = 20,
        nombre: Optional[str] = None,
        dni: Optional[str] = None,
        estado: Optional[EstadoEnum] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de clientes con filtros opcionales"""
    # USAR EL MODELO (ClienteModel), NO EL ESQUEMA (Cliente)
    query = db.query(ClienteModel)  # ← CAMBIO AQUÍ

    if nombre:
        query = query.filter(ClienteModel.nombre.contains(nombre))
    if dni:
        query = query.filter(ClienteModel.dni == dni)
    if estado:
        query = query.filter(ClienteModel.estado == estado)

    clientes = query.offset(skip).limit(limit).all()
    return clientes


# EJEMPLO CORREGIDO - Endpoint de stats
@app.get("/clientes", response_model=List[Cliente])
async def get_clientes(
        skip: int = 0,
        limit: int = 20,
        nombre: Optional[str] = None,
        dni: Optional[str] = None,
        estado: Optional[EstadoEnum] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de clientes con filtros opcionales"""
    # USAR EL MODELO (ClienteModel), NO EL ESQUEMA (Cliente)
    query = db.query(ClienteModel)  # ← CAMBIO AQUÍ

    if nombre:
        query = query.filter(ClienteModel.nombre.contains(nombre))
    if dni:
        query = query.filter(ClienteModel.dni == dni)
    if estado:
        query = query.filter(ClienteModel.estado == estado)

    clientes = query.offset(skip).limit(limit).all()
    return clientes


@app.get("/clientes/{cliente_id}", response_model=ClienteConMascotas)
async def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente específico con sus mascotas"""
    cliente = db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@app.post("/clientes", response_model=Cliente)
async def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    # Verificar que el DNI no exista
    existing_cliente = db.query(Cliente).filter(Cliente.dni == cliente.dni).first()
    if existing_cliente:
        raise HTTPException(status_code=400, detail="DNI ya existe")

    # Verificar que el email no exista
    existing_email = db.query(Cliente).filter(Cliente.email == cliente.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email ya existe")

    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


# ================================
# ENDPOINTS DE MASCOTAS
# ================================

@app.get("/mascotas", response_model=List[MascotaConCliente])
async def get_mascotas(
        skip: int = 0,
        limit: int = 20,
        nombre: Optional[str] = None,
        id_cliente: Optional[int] = None,
        sexo: Optional[SexoMascotaEnum] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de mascotas con filtros"""
    query = db.query(Mascota)

    if nombre:
        query = query.filter(Mascota.nombre.contains(nombre))
    if id_cliente:
        query = query.filter(Mascota.id_cliente == id_cliente)
    if sexo:
        query = query.filter(Mascota.sexo == sexo)

    mascotas = query.offset(skip).limit(limit).all()
    return mascotas


@app.get("/mascotas/{mascota_id}", response_model=MascotaConCliente)
async def get_mascota(mascota_id: int, db: Session = Depends(get_db)):
    """Obtener una mascota específica"""
    mascota = db.query(Mascota).filter(Mascota.id_mascota == mascota_id).first()
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return mascota


@app.post("/mascotas", response_model=Mascota)
async def create_mascota(mascota: MascotaCreate, db: Session = Depends(get_db)):
    """Crear una nueva mascota"""
    # Verificar que el cliente existe
    cliente = db.query(Cliente).filter(Cliente.id_cliente == mascota.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Verificar que la raza existe
    raza = db.query(Raza).filter(Raza.id_raza == mascota.id_raza).first()
    if not raza:
        raise HTTPException(status_code=404, detail="Raza no encontrada")

    db_mascota = Mascota(**mascota.dict())
    db.add(db_mascota)
    db.commit()
    db.refresh(db_mascota)
    return db_mascota


# ================================
# ENDPOINTS DE VETERINARIOS
# ================================

@app.get("/veterinarios", response_model=List[VeterinarioConEspecialidad])
async def get_veterinarios(
        skip: int = 0,
        limit: int = 20,
        especialidad: Optional[int] = None,
        turno: Optional[TurnoEnum] = None,
        disposicion: Optional[DisposicionEnum] = None,
        estado: Optional[EstadoEnum] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de veterinarios con filtros"""
    query = db.query(Veterinario)

    if especialidad:
        query = query.filter(Veterinario.id_especialidad == especialidad)
    if turno:
        query = query.filter(Veterinario.turno == turno)
    if disposicion:
        query = query.filter(Veterinario.disposicion == disposicion)
    if estado:
        query = query.filter(Veterinario.estado == estado)

    veterinarios = query.offset(skip).limit(limit).all()
    return veterinarios


@app.get("/veterinarios/{veterinario_id}", response_model=VeterinarioConEspecialidad)
async def get_veterinario(veterinario_id: int, db: Session = Depends(get_db)):
    """Obtener un veterinario específico"""
    veterinario = db.query(Veterinario).filter(Veterinario.id_veterinario == veterinario_id).first()
    if veterinario is None:
        raise HTTPException(status_code=404, detail="Veterinario no encontrado")
    return veterinario


# ================================
# ENDPOINTS DE CONSULTAS
# ================================

@app.get("/consultas", response_model=List[ConsultaCompleta])
async def get_consultas(
        skip: int = 0,
        limit: int = 20,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        id_veterinario: Optional[int] = None,
        condicion_general: Optional[CondicionGeneralEnum] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de consultas con filtros"""
    query = db.query(Consulta)

    if fecha_desde:
        query = query.filter(Consulta.fecha_consulta >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Consulta.fecha_consulta <= fecha_hasta)
    if id_veterinario:
        query = query.filter(Consulta.id_veterinario == id_veterinario)
    if condicion_general:
        query = query.filter(Consulta.condicion_general == condicion_general)

    consultas = query.order_by(Consulta.fecha_consulta.desc()).offset(skip).limit(limit).all()
    return consultas


@app.get("/consultas/{consulta_id}", response_model=ConsultaCompleta)
async def get_consulta(consulta_id: int, db: Session = Depends(get_db)):
    """Obtener una consulta específica"""
    consulta = db.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()
    if consulta is None:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return consulta


# ================================
# ENDPOINTS DE CITAS
# ================================

@app.get("/citas", response_model=List[CitaCompleta])
async def get_citas(
        skip: int = 0,
        limit: int = 20,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado_cita: Optional[str] = None,
        id_mascota: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de citas con filtros"""
    query = db.query(Cita)

    if fecha_desde:
        query = query.filter(Cita.fecha_hora_programada >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Cita.fecha_hora_programada <= fecha_hasta)
    if estado_cita:
        query = query.filter(Cita.estado_cita == estado_cita)
    if id_mascota:
        query = query.filter(Cita.id_mascota == id_mascota)

    citas = query.order_by(Cita.fecha_hora_programada.asc()).offset(skip).limit(limit).all()
    return citas


@app.get("/citas/hoy")
async def get_citas_hoy(db: Session = Depends(get_db)):
    """Obtener citas programadas para hoy"""
    hoy = date.today()
    citas = db.query(Cita).filter(
        Cita.fecha_hora_programada >= hoy,
        Cita.fecha_hora_programada < hoy.replace(day=hoy.day + 1),
        Cita.estado_cita == "Programada"
    ).all()
    return citas


# ================================
# ENDPOINTS DE SERVICIOS
# ================================

@app.get("/servicios", response_model=List[ServicioConTipo])
async def get_servicios(
        skip: int = 0,
        limit: int = 50,
        activo: Optional[bool] = True,
        id_tipo_servicio: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """Obtener lista de servicios"""
    query = db.query(Servicio)

    if activo is not None:
        query = query.filter(Servicio.activo == activo)
    if id_tipo_servicio:
        query = query.filter(Servicio.id_tipo_servicio == id_tipo_servicio)

    servicios = query.offset(skip).limit(limit).all()
    return servicios


# ================================
# ENDPOINTS DE RAZAS Y TIPOS
# ================================

@app.get("/razas", response_model=List[Raza])
async def get_razas(db: Session = Depends(get_db)):
    """Obtener todas las razas"""
    razas = db.query(Raza).all()
    return razas


@app.get("/especialidades", response_model=List[Especialidad])
async def get_especialidades(db: Session = Depends(get_db)):
    """Obtener todas las especialidades"""
    especialidades = db.query(Especialidad).all()
    return especialidades


@app.get("/tipos-servicio", response_model=List[TipoServicio])
async def get_tipos_servicio(db: Session = Depends(get_db)):
    """Obtener todos los tipos de servicio"""
    tipos = db.query(TipoServicio).all()
    return tipos


# ================================
# ENDPOINTS DE ESTADÍSTICAS
# ================================

@app.get("/stats", response_model=EstadisticasVeterinaria)
async def get_estadisticas(db: Session = Depends(get_db)):
    """Estadísticas generales del sistema"""
    return {
        "total_clientes": db.query(ClienteModel).count(),  # ← CAMBIO AQUÍ
        "total_mascotas": db.query(MascotaModel).count(),  # ← CAMBIO AQUÍ
        "total_veterinarios": db.query(VeterinarioModel).count(),  # ← CAMBIO AQUÍ
        "total_consultas": db.query(ConsultaModel).count(),  # ← CAMBIO AQUÍ
        "total_citas_pendientes": db.query(CitaModel).filter(CitaModel.estado_cita == "Programada").count(),
        "total_servicios_activos": db.query(ServicioModel).filter(ServicioModel.activo == True).count()
    }


@app.get("/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Datos para dashboard principal"""
    hoy = date.today()

    # Citas de hoy
    citas_hoy = db.query(Cita).filter(
        Cita.fecha_hora_programada >= hoy,
        Cita.fecha_hora_programada < hoy.replace(day=hoy.day + 1)
    ).count()

    # Veterinarios disponibles
    veterinarios_libres = db.query(Veterinario).filter(
        Veterinario.disposicion == "Libre",
        Veterinario.estado == "Activo"
    ).count()

    return {
        "estadisticas_generales": {
            "total_clientes": db.query(Cliente).count(),
            "total_mascotas": db.query(Mascota).count(),
            "total_veterinarios": db.query(Veterinario).count(),
            "total_consultas": db.query(Consulta).count(),
            "total_citas_pendientes": db.query(Cita).filter(Cita.estado_cita == "Programada").count(),
            "total_servicios_activos": db.query(Servicio).filter(Servicio.activo == True).count()
        },
        "citas_hoy": citas_hoy,
        "veterinarios_disponibles": veterinarios_libres,
        "timestamp": datetime.now().isoformat()
    }


# ================================
# ENDPOINTS DE BÚSQUEDA
# ================================

@app.get("/search/clientes")
async def search_clientes(
        q: str = Query(..., min_length=2, description="Término de búsqueda"),
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """Búsqueda de clientes por nombre, DNI o email"""
    clientes = db.query(Cliente).filter(
        (Cliente.nombre.contains(q)) |
        (Cliente.apellido_paterno.contains(q)) |
        (Cliente.dni.contains(q)) |
        (Cliente.email.contains(q))
    ).limit(limit).all()

    return clientes


@app.get("/search/mascotas")
async def search_mascotas(
        q: str = Query(..., min_length=2, description="Término de búsqueda"),
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """Búsqueda de mascotas por nombre"""
    mascotas = db.query(Mascota).filter(
        Mascota.nombre.contains(q)
    ).limit(limit).all()

    return mascotas