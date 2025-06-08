# app/schemas/veterinaria.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ========================================
# ENUMS
# ========================================

class TipoAnimalEnum(str, Enum):
    PERRO = "Perro"
    GATO = "Gato"


class EstadoEnum(str, Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"


class TurnoEnum(str, Enum):
    MANANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"


class GeneroEnum(str, Enum):
    F = "F"
    M = "M"


class SexoMascotaEnum(str, Enum):
    MACHO = "Macho"
    HEMBRA = "Hembra"


class TipoVeterinarioEnum(str, Enum):
    MEDICO_GENERAL = "Medico General"
    ESPECIALIZADO = "Especializado"


class DisposicionEnum(str, Enum):
    OCUPADO = "Ocupado"
    LIBRE = "Libre"


class TipoSolicitudEnum(str, Enum):
    CONSULTA_URGENTE = "Consulta urgente"
    CONSULTA_NORMAL = "Consulta normal"
    SERVICIO_PROGRAMADO = "Servicio programado"


class EstadoSolicitudEnum(str, Enum):
    PENDIENTE = "Pendiente"
    EN_TRIAJE = "En triaje"
    EN_ATENCION = "En atencion"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"


class CondicionCorporalEnum(str, Enum):
    MUY_DELGADO = "Muy delgado"
    DELGADO = "Delgado"
    IDEAL = "Ideal"
    SOBREPESO = "Sobrepeso"
    OBESO = "Obeso"


class ClasificacionUrgenciaEnum(str, Enum):
    NO_URGENTE = "No urgente"
    POCO_URGENTE = "Poco urgente"
    URGENTE = "Urgente"
    MUY_URGENTE = "Muy urgente"
    CRITICO = "Critico"


class CondicionGeneralEnum(str, Enum):
    EXCELENTE = "Excelente"
    BUENA = "Buena"
    REGULAR = "Regular"
    MALA = "Mala"
    CRITICA = "Critica"


# ========================================
# SCHEMAS BASE
# ========================================

class TipoServicioBase(BaseModel):
    descripcion: str


class TipoServicio(TipoServicioBase):
    id_tipo_servicio: int

    class Config:
        from_attributes = True


class EspecialidadBase(BaseModel):
    descripcion: str


class Especialidad(EspecialidadBase):
    id_especialidad: int

    class Config:
        from_attributes = True


class RazaBase(BaseModel):
    nombre_raza: str


class Raza(RazaBase):
    id_raza: int

    class Config:
        from_attributes = True


class TipoAnimalBase(BaseModel):
    id_raza: int
    descripcion: TipoAnimalEnum


class TipoAnimal(TipoAnimalBase):
    id_tipo_animal: int

    class Config:
        from_attributes = True


class ClienteBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr
    direccion: Optional[str] = None
    estado: Optional[EstadoEnum] = None

    @validator('dni')
    def validate_dni(cls, v):
        if len(v) != 8 or not v.isdigit():
            raise ValueError('DNI debe tener 8 dígitos')
        return v

    @validator('telefono')
    def validate_telefono(cls, v):
        if len(v) != 9 or not v.startswith('9'):
            raise ValueError('Teléfono debe tener 9 dígitos y empezar con 9')
        return v


class Cliente(ClienteBase):
    id_cliente: int
    fecha_registro: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClienteCreate(ClienteBase):
    pass


class RecepcionistaBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr
    fecha_ingreso: Optional[date] = None
    turno: Optional[TurnoEnum] = None
    estado: Optional[EstadoEnum] = None
    contraseña: str
    genero: GeneroEnum


class Recepcionista(RecepcionistaBase):
    id_recepcionista: int

    class Config:
        from_attributes = True


class MascotaBase(BaseModel):
    id_cliente: int
    id_raza: int
    nombre: str
    sexo: SexoMascotaEnum
    color: Optional[str] = None
    edad_anios: Optional[int] = None
    edad_meses: Optional[int] = None
    esterilizado: Optional[bool] = False
    imagen: Optional[str] = None


class Mascota(MascotaBase):
    id_mascota: int

    class Config:
        from_attributes = True


class MascotaCreate(MascotaBase):
    pass


class ServicioBase(BaseModel):
    id_tipo_servicio: int
    nombre_servicio: str
    precio: Decimal
    activo: Optional[bool] = True


class Servicio(ServicioBase):
    id_servicio: int

    class Config:
        from_attributes = True


class VeterinarioBase(BaseModel):
    id_especialidad: int
    codigo_CMVP: str
    tipo_veterinario: TipoVeterinarioEnum
    fecha_nacimiento: date
    genero: GeneroEnum
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    dni: str
    telefono: str
    email: EmailStr
    estado: Optional[EstadoEnum] = EstadoEnum.ACTIVO
    fecha_ingreso: date
    disposicion: Optional[DisposicionEnum] = DisposicionEnum.LIBRE
    turno: TurnoEnum
    contraseña: str


class Veterinario(VeterinarioBase):
    id_veterinario: int

    class Config:
        from_attributes = True


class SolicitudAtencionBase(BaseModel):
    id_mascota: Optional[int] = None
    id_recepcionista: Optional[int] = None
    fecha_hora_solicitud: Optional[datetime] = None
    tipo_solicitud: TipoSolicitudEnum
    estado: Optional[EstadoSolicitudEnum] = EstadoSolicitudEnum.PENDIENTE


class SolicitudAtencion(SolicitudAtencionBase):
    id_solicitud: int

    class Config:
        from_attributes = True


class TriajeBase(BaseModel):
    id_solicitud: int
    id_veterinario: int
    fecha_hora_triaje: datetime
    peso_mascota: Decimal
    latido_por_minuto: int
    frecuencia_respiratoria_rpm: int
    temperatura: Decimal
    talla: Optional[Decimal] = None
    tiempo_capilar: Optional[str] = None
    color_mucosas: Optional[str] = None
    frecuencia_pulso: int
    porce_deshidratacion: Optional[Decimal] = None
    condicion_corporal: Optional[CondicionCorporalEnum] = CondicionCorporalEnum.IDEAL
    clasificacion_urgencia: ClasificacionUrgenciaEnum


class Triaje(TriajeBase):
    id_triaje: int

    class Config:
        from_attributes = True


class ConsultaBase(BaseModel):
    id_triaje: int
    id_veterinario: int
    tipo_consulta: str
    fecha_consulta: datetime
    motivo_consulta: Optional[str] = None
    sintomas_observados: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None
    observaciones: Optional[str] = None
    condicion_general: CondicionGeneralEnum
    es_seguimiento: Optional[bool] = False


class Consulta(ConsultaBase):
    id_consulta: int

    class Config:
        from_attributes = True


class PatologiaBase(BaseModel):
    nombre_patologia: str
    especie_afecta: TipoAnimalEnum
    gravedad: Optional[str] = "Moderada"
    es_cronica: Optional[bool] = None
    es_contagiosa: Optional[bool] = None


class Patologia(PatologiaBase):
    id_patologia: int

    class Config:
        from_attributes = True


# ========================================
# SCHEMAS CON RELACIONES
# ========================================

class MascotaConCliente(Mascota):
    cliente: Optional[Cliente] = None
    raza: Optional[Raza] = None


class ClienteConMascotas(Cliente):
    mascotas: List[Mascota] = []


class VeterinarioConEspecialidad(Veterinario):
    especialidad: Optional[Especialidad] = None


class ServicioConTipo(Servicio):
    tipo_servicio: Optional[TipoServicio] = None


class ConsultaCompleta(Consulta):
    triaje: Optional[Triaje] = None
    veterinario: Optional[Veterinario] = None


class TriajeCompleto(Triaje):
    solicitud: Optional[SolicitudAtencion] = None
    veterinario: Optional[Veterinario] = None


# ========================================
# SCHEMAS PARA ESTADÍSTICAS
# ========================================

class EstadisticasVeterinaria(BaseModel):
    total_clientes: int
    total_mascotas: int
    total_veterinarios: int
    total_consultas: int
    total_citas_pendientes: int
    total_servicios_activos: int


class EstadisticasMascota(BaseModel):
    total_por_especie: dict
    total_por_raza: dict
    promedio_edad: float
    total_esterilizadas: int


# ========================================
# SCHEMAS PARA RESPONSES COMPLEJAS
# ========================================

class HistorialClinicoBase(BaseModel):
    id_mascota: Optional[int] = None
    id_consulta: Optional[int] = None
    id_diagnostico: Optional[int] = None
    id_tratamiento: Optional[int] = None
    id_veterinario: Optional[int] = None
    fecha_evento: datetime
    tipo_evento: str
    edad_meses: Optional[int] = None
    descripcion_evento: str
    peso_momento: Optional[Decimal] = None
    observaciones: Optional[str] = None


class HistorialClinico(HistorialClinicoBase):
    id_historial: int

    class Config:
        from_attributes = True


class DiagnosticoBase(BaseModel):
    id_consulta: Optional[int] = None
    id_patologia: Optional[int] = None
    tipo_diagnostico: str = "Presuntivo"
    fecha_diagnostico: datetime
    estado_patologia: str = "Activa"
    diagnostico: str


class Diagnostico(DiagnosticoBase):
    id_diagnostico: int

    class Config:
        from_attributes = True


class TratamientoBase(BaseModel):
    id_consulta: Optional[int] = None
    id_patologia: Optional[int] = None
    fecha_inicio: date
    eficacia_tratamiento: Optional[str] = None
    tipo_tratamiento: str


class Tratamiento(TratamientoBase):
    id_tratamiento: int

    class Config:
        from_attributes = True


class CitaBase(BaseModel):
    id_mascota: Optional[int] = None
    id_servicio: Optional[int] = None
    id_servicio_solicitado: Optional[int] = None
    fecha_hora_programada: datetime
    estado_cita: Optional[str] = "Programada"
    requiere_ayuno: Optional[bool] = None
    observaciones: Optional[str] = None


class Cita(CitaBase):
    id_cita: int

    class Config:
        from_attributes = True


class CitaCompleta(Cita):
    mascota: Optional[Mascota] = None
    servicio: Optional[Servicio] = None


class ServicioSolicitadoBase(BaseModel):
    id_consulta: Optional[int] = None
    id_servicio: Optional[int] = None
    fecha_solicitado: Optional[datetime] = None
    prioridad: Optional[str] = None
    estado_examen: Optional[str] = "Solicitado"
    comentario_opcional: Optional[str] = None


class ServicioSolicitado(ServicioSolicitadoBase):
    id_servicio_solicitado: int

    class Config:
        from_attributes = True


class ResultadoServicioBase(BaseModel):
    id_cita: Optional[int] = None
    id_veterinario: Optional[int] = None
    resultado: str
    interpretacion: Optional[str] = None
    archivo_adjunto: Optional[str] = None
    fecha_realizacion: datetime


class ResultadoServicio(ResultadoServicioBase):
    id_resultado: int

    class Config:
        from_attributes = True


# ========================================
# SCHEMAS PARA BÚSQUEDAS Y FILTROS
# ========================================

class FiltroMascota(BaseModel):
    nombre: Optional[str] = None
    id_cliente: Optional[int] = None
    id_raza: Optional[int] = None
    sexo: Optional[SexoMascotaEnum] = None
    esterilizado: Optional[bool] = None


class FiltroCliente(BaseModel):
    nombre: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[str] = None
    estado: Optional[EstadoEnum] = None


class FiltroVeterinario(BaseModel):
    nombre: Optional[str] = None
    id_especialidad: Optional[int] = None
    tipo_veterinario: Optional[TipoVeterinarioEnum] = None
    turno: Optional[TurnoEnum] = None
    disposicion: Optional[DisposicionEnum] = None
    estado: Optional[EstadoEnum] = None


class FiltroConsulta(BaseModel):
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    id_veterinario: Optional[int] = None
    id_mascota: Optional[int] = None
    condicion_general: Optional[CondicionGeneralEnum] = None


class FiltroCita(BaseModel):
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    estado_cita: Optional[str] = None
    id_mascota: Optional[int] = None
    id_servicio: Optional[int] = None


# ========================================
# SCHEMAS PARA REPORTES
# ========================================

class ReporteConsultas(BaseModel):
    periodo: str
    total_consultas: int
    consultas_por_veterinario: dict
    consultas_por_especialidad: dict
    promedio_consultas_dia: float


class ReporteCitas(BaseModel):
    periodo: str
    total_citas: int
    citas_atendidas: int
    citas_canceladas: int
    servicios_mas_solicitados: dict


class ReporteFinanciero(BaseModel):
    periodo: str
    ingresos_servicios: Decimal
    servicios_por_categoria: dict
    promedio_ingreso_dia: Decimal


# ========================================
# SCHEMAS PARA DASHBOARD
# ========================================

class DashboardData(BaseModel):
    estadisticas_generales: EstadisticasVeterinaria
    citas_hoy: List[CitaCompleta]
    consultas_pendientes: int
    veterinarios_disponibles: int
    urgencias_criticas: int


# ========================================
# SCHEMAS PARA AUTENTICACIÓN
# ========================================

class LoginRequest(BaseModel):
    email: EmailStr
    contraseña: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_data: dict


class UsuarioActual(BaseModel):
    id: int
    nombre: str
    email: str
    tipo_usuario: str  # "veterinario", "recepcionista"


# ========================================
# SCHEMAS PARA RESPUESTAS API
# ========================================

class ResponseMessage(BaseModel):
    message: str
    status: str = "success"


class ErrorResponse(BaseModel):
    message: str
    status: str = "error"
    details: Optional[dict] = None


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool