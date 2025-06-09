# app/schemas/solicitud_schema.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from .base_schema import BaseResponse, PaginationResponse

# ===== ENUMS =====
TIPO_SOLICITUD_CHOICES = ['Consulta urgente', 'Consulta normal', 'Servicio programado']
ESTADO_SOLICITUD_CHOICES = ['Pendiente', 'En triaje', 'En atencion', 'Completada', 'Cancelada']


# ===== SCHEMAS DE INPUT (REQUEST) =====

class SolicitudCreate(BaseModel):
    """Schema para crear una solicitud de atención"""
    id_mascota: int
    id_recepcionista: int
    tipo_solicitud: str
    estado: Optional[str] = "Pendiente"

    # Validators
    @validator('tipo_solicitud')
    def validate_tipo_solicitud(cls, v):
        if v not in TIPO_SOLICITUD_CHOICES:
            raise ValueError(f'Tipo de solicitud debe ser una de: {", ".join(TIPO_SOLICITUD_CHOICES)}')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        if v and v not in ESTADO_SOLICITUD_CHOICES:
            raise ValueError(f'Estado debe ser uno de: {", ".join(ESTADO_SOLICITUD_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "id_mascota": 1,
                "id_recepcionista": 1,
                "tipo_solicitud": "Consulta urgente",
                "estado": "Pendiente"
            }
        }


class SolicitudUpdate(BaseModel):
    """Schema para actualizar una solicitud de atención"""
    tipo_solicitud: Optional[str] = None
    estado: Optional[str] = None

    # Validators
    @validator('tipo_solicitud')
    def validate_tipo_solicitud(cls, v):
        if v and v not in TIPO_SOLICITUD_CHOICES:
            raise ValueError(f'Tipo de solicitud debe ser una de: {", ".join(TIPO_SOLICITUD_CHOICES)}')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        if v and v not in ESTADO_SOLICITUD_CHOICES:
            raise ValueError(f'Estado debe ser uno de: {", ".join(ESTADO_SOLICITUD_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "tipo_solicitud": "Consulta normal",
                "estado": "En triaje"
            }
        }


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class SolicitudResponse(BaseResponse):
    """Schema para devolver información de solicitud"""
    id_solicitud: int
    id_mascota: int
    id_recepcionista: int
    fecha_hora_solicitud: datetime
    tipo_solicitud: str
    estado: str

    class Config:
        schema_extra = {
            "example": {
                "id_solicitud": 1,
                "id_mascota": 1,
                "id_recepcionista": 1,
                "fecha_hora_solicitud": "2024-01-15T10:30:00",
                "tipo_solicitud": "Consulta urgente",
                "estado": "Pendiente"
            }
        }


class SolicitudWithDetailsResponse(BaseResponse):
    """Schema para solicitud con detalles de mascota y recepcionista"""
    id_solicitud: int
    id_mascota: int
    id_recepcionista: int
    fecha_hora_solicitud: datetime
    tipo_solicitud: str
    estado: str
    mascota_nombre: Optional[str]
    cliente_nombre: Optional[str]
    recepcionista_nombre: Optional[str]


class SolicitudListResponse(PaginationResponse):
    """Schema para lista de solicitudes"""
    solicitudes: List[SolicitudResponse]


# ===== SCHEMAS DE BÚSQUEDA =====

class SolicitudSearch(BaseModel):
    """Schema para búsqueda de solicitudes"""
    id_mascota: Optional[int] = None
    id_recepcionista: Optional[int] = None
    tipo_solicitud: Optional[str] = None
    estado: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    page: int = 1
    per_page: int = 20

    @validator('tipo_solicitud')
    def validate_tipo_solicitud(cls, v):
        if v and v not in TIPO_SOLICITUD_CHOICES:
            raise ValueError(f'Tipo de solicitud debe ser una de: {", ".join(TIPO_SOLICITUD_CHOICES)}')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        if v and v not in ESTADO_SOLICITUD_CHOICES:
            raise ValueError(f'Estado debe ser uno de: {", ".join(ESTADO_SOLICITUD_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "tipo_solicitud": "Consulta urgente",
                "estado": "Pendiente",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-01-31",
                "page": 1,
                "per_page": 20
            }
        }


# ===== SCHEMAS ESPECIALES =====

class EstadisticasSolicitud(BaseModel):
    """Schema para estadísticas de solicitudes"""
    total: int
    pendientes: int
    en_triaje: int
    en_atencion: int
    completadas: int
    canceladas: int
    porcentajes: dict


class EstadisticasTipo(BaseModel):
    """Schema para estadísticas por tipo"""
    total: int
    consultas_urgentes: int
    consultas_normales: int
    servicios_programados: int
    porcentajes: dict


class ResumenDiario(BaseModel):
    """Schema para resumen diario"""
    fecha: date
    total: int
    urgentes: int
    pendientes: int
    completadas: int
    tasa_completion: float


class CambioEstado(BaseModel):
    """Schema para cambio de estado"""
    nuevo_estado: str

    @validator('nuevo_estado')
    def validate_nuevo_estado(cls, v):
        if v not in ESTADO_SOLICITUD_CHOICES:
            raise ValueError(f'Estado debe ser uno de: {", ".join(ESTADO_SOLICITUD_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "nuevo_estado": "En triaje"
            }
        }


# ===== SCHEMAS PARA FLUJO DE TRABAJO =====

class FlujoSolicitud(BaseModel):
    """Schema para seguimiento del flujo de solicitud"""
    id_solicitud: int
    estado_actual: str
    estados_posibles: List[str]
    tiempo_en_estado: Optional[int]  # minutos
    puede_avanzar: bool

    @validator('estados_posibles')
    def validate_estados_posibles(cls, v):
        for estado in v:
            if estado not in ESTADO_SOLICITUD_CHOICES:
                raise ValueError(f'Estados deben ser de: {", ".join(ESTADO_SOLICITUD_CHOICES)}')
        return v