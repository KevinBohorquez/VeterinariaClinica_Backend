# main.py (VERSIÓN CORREGIDA COMPLETA)
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
    Cita as CitaModel
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
        "status": "OK"
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
        # Usar MODELOS, no esquemas
        total_clientes = db.query(ClienteModel).count()
        total_mascotas = db.query(MascotaModel).count()
        total_veterinarios = db.query(VeterinarioModel).count()

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
    query = db.query(ClienteModel)

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
    cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.post("/clientes", response_model=Cliente)
async def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    # Verificar que el DNI no exista
    existing_cliente = db.query(ClienteModel).filter(ClienteModel.dni == cliente.dni).first()
    if existing_cliente:
        raise HTTPException(status_code=400, detail="DNI ya existe")

    # Verificar que el email no exista
    existing_email = db.query(ClienteModel).filter(ClienteModel.email == cliente.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email ya existe")

    db_cliente = ClienteModel(**cliente.dict())
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
    query = db.query(MascotaModel)

    if nombre:
        query = query.filter(MascotaModel.nombre.contains(nombre))
    if id_cliente:
        query = query.filter(MascotaModel.id_cliente == id_cliente)
    if sexo:
        query = query.filter(MascotaModel.sexo == sexo)

    mascotas = query.offset(skip).limit(limit).all()
    return mascotas

@app.get("/mascotas/{mascota_id}", response_model=MascotaConCliente)
async def get_mascota(mascota_id: int, db: Session = Depends(get_db)):
    """Obtener una mascota específica"""
    mascota = db.query(MascotaModel).filter(MascotaModel.id_mascota == mascota_id).first()
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return mascota

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
    query = db.query(VeterinarioModel)

    if especialidad:
        query = query.filter(VeterinarioModel.id_especialidad == especialidad)
    if turno:
        query = query.filter(VeterinarioModel.turno == turno)
    if disposicion:
        query = query.filter(VeterinarioModel.disposicion == disposicion)
    if estado:
        query = query.filter(VeterinarioModel.estado == estado)

    veterinarios = query.offset(skip).limit(limit).all()
    return veterinarios

# ================================
# ENDPOINTS DE RAZAS Y TIPOS
# ================================

@app.get("/razas", response_model=List[Raza])
async def get_razas(db: Session = Depends(get_db)):
    """Obtener todas las razas"""
    razas = db.query(RazaModel).all()
    return razas

@app.get("/especialidades", response_model=List[Especialidad])
async def get_especialidades(db: Session = Depends(get_db)):
    """Obtener todas las especialidades"""
    especialidades = db.query(EspecialidadModel).all()
    return especialidades

# ================================
# ENDPOINTS DE ESTADÍSTICAS
# ================================

@app.get("/stats", response_model=EstadisticasVeterinaria)
async def get_estadisticas(db: Session = Depends(get_db)):
    """Estadísticas generales del sistema"""
    return {
        "total_clientes": db.query(ClienteModel).count(),
        "total_mascotas": db.query(MascotaModel).count(),
        "total_veterinarios": db.query(VeterinarioModel).count(),
        "total_consultas": db.query(ConsultaModel).count(),
        "total_citas_pendientes": db.query(CitaModel).filter(CitaModel.estado_cita == "Programada").count(),
        "total_servicios_activos": db.query(ServicioModel).filter(ServicioModel.activo == True).count()
    }