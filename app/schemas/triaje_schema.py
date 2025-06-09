# app/schemas/triaje_schema.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from .base_schema import BaseResponse, PaginationResponse

# ===== ENUMS =====
CONDICION_CORPORAL_CHOICES = ['Muy delgado', 'Delgado', 'Ideal', 'Sobrepeso', 'Obeso']
CLASIFICACION_URGENCIA_CHOICES = ['No urgente', 'Poco urgente', 'Urgente', 'Muy urgente', 'Critico']


# ===== SCHEMAS DE INPUT (REQUEST) =====

class TriajeCreate(BaseModel):
    """Schema para crear un triaje"""
    id_solicitud: int
    id_veterinario: int
    peso_mascota: Decimal
    latido_por_minuto: int
    frecuencia_respiratoria_rpm: int
    temperatura: Decimal
    talla: Optional[Decimal] = None
    tiempo_capilar: Optional[str] = None
    color_mucosas: Optional[str] = None
    frecuencia_pulso: int
    porce_deshidratacion: Optional[Decimal] = None
    condicion_corporal: Optional[str] = "Ideal"
    clasificacion_urgencia: str

    # Validators
    @validator('peso_mascota')
    def validate_peso(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('El peso debe estar entre 0.01 y 100 kg')
        return v

    @validator('latido_por_minuto')
    def validate_latidos(cls, v):
        if v < 40 or v > 300:
            raise ValueError('Los latidos por minuto deben estar entre 40 y 300')
        return v

    @validator('frecuencia_respiratoria_rpm')
    def validate_respiracion(cls, v):
        if v < 10 or v > 150:
            raise ValueError('La frecuencia respiratoria debe estar entre 10 y 150 rpm')
        return v

    @validator('temperatura')
    def validate_temperatura(cls, v):
        if v < 35.0 or v > 42.0:
            raise ValueError('La temperatura debe estar entre 35.0 y 42.0 °C')
        return v

    @validator('talla')
    def validate_talla(cls, v):
        if v is not None and (v <= 0 or v > 200):
            raise ValueError('La talla debe estar entre 0.01 y 200 cm')
        return v

    @validator('frecuencia_pulso')
    def validate_pulso(cls, v):
        if v < 30 or v > 250:
            raise ValueError('La frecuencia de pulso debe estar entre 30 y 250')
        return v

    @validator('porce_deshidratacion')
    def validate_deshidratacion(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('El porcentaje de deshidratación debe estar entre 0 y 100')
        return v

    @validator('condicion_corporal')
    def validate_condicion_corporal(cls, v):
        if v and v not in CONDICION_CORPORAL_CHOICES:
            raise ValueError(f'Condición corporal debe ser una de: {", ".join(CONDICION_CORPORAL_CHOICES)}')
        return v

    @validator('clasificacion_urgencia')
    def validate_clasificacion_urgencia(cls, v):
        if v not in CLASIFICACION_URGENCIA_CHOICES:
            raise ValueError(f'Clasificación de urgencia debe ser una de: {", ".join(CLASIFICACION_URGENCIA_CHOICES)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "id_solicitud": 1,
                "id_veterinario": 1,
                "peso_mascota": 15.5,
                "latido_por_minuto": 120,
                "frecuencia_respiratoria_rpm": 24,
                "temperatura": 38.5,
                "talla": 45.0,
                "tiempo_capilar": "< 2 segundos",
                "color_mucosas": "Rosadas",
                "frecuencia_pulso": 110,
                "porce_deshidratacion": 5.0,
                "condicion_corporal": "Ideal",
                "clasificacion_urgencia": "Urgente"
            }
        }


class TriajeUpdate(BaseModel):
    """Schema para actualizar un triaje"""
    peso_mascota: Optional[Decimal] = None
    latido_por_minuto: Optional[int] = None
    frecuencia_respiratoria_rpm: Optional[int] = None
    temperatura: Optional[Decimal] = None
    talla: Optional[Decimal] = None
    tiempo_capilar: Optional[str] = None
    color_mucosas: Optional[str] = None
    frecuencia_pulso: Optional[int] = None
    porce_deshidratacion: Optional[Decimal] = None
    condicion_corporal: Optional[str] = None
    clasificacion_urgencia: Optional[str] = None

    # Mismos validators que Create pero opcionales
    @validator('peso_mascota')
    def validate_peso(cls, v):
        if v is not None and (v <= 0 or v > 100):
            raise ValueError('El peso debe estar entre 0.01 y 100 kg')
        return v

    @validator('latido_por_minuto')
    def validate_latidos(cls, v):
        if v is not None and (v < 40 or v > 300):
            raise ValueError('Los latidos por minuto deben estar entre 40 y 300')
        return v


# ===== SCHEMAS DE OUTPUT (RESPONSE) =====

class TriajeResponse(BaseResponse):
    """Schema para devolver información de triaje"""
    id_triaje: int
    id_solicitud: int
    id_veterinario: int
    fecha_hora_triaje: datetime
    peso_mascota: Decimal
    latido_por_minuto: int
    frecuencia_respiratoria_rpm: int
    temperatura: Decimal
    talla: Optional[Decimal]
    tiempo_capilar: Optional[str]
    color_mucosas: Optional[str]
    frecuencia_pulso: int
    porce_deshidratacion: Optional[Decimal]
    condicion_corporal: Optional[str]
    clasificacion_urgencia: str


class TriajeListResponse(PaginationResponse):
    """Schema para lista de triajes"""
    triajes: List[TriajeResponse]


# ===== SCHEMAS DE BÚSQUEDA =====

class TriajeSearch(BaseModel):
    """Schema para búsqueda de triajes"""
    id_veterinario: Optional[int] = None
    clasificacion_urgencia: Optional[str] = None
    condicion_corporal: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    peso_min: Optional[Decimal] = None
    peso_max: Optional[Decimal] = None
    page: int = 1
    per_page: int = 20

    @validator('clasificacion_urgencia')
    def validate_clasificacion_urgencia(cls, v):
        if v and v not in CLASIFICACION_URGENCIA_CHOICES:
            raise ValueError(f'Clasificación de urgencia debe ser una de: {", ".join(CLASIFICACION_URGENCIA_CHOICES)}')
        return v


# ===== SCHEMAS ESPECIALES =====

class EstadisticasUrgencia(BaseModel):
    """Schema para estadísticas de urgencia"""
    total: int
    criticos: int
    muy_urgentes: int
    urgentes: int
    poco_urgentes: int
    no_urgentes: int
    porcentajes: dict


class PromediosSignosVitales(BaseModel):
    """Schema para promedios de signos vitales"""
    peso_promedio: float
    latidos_promedio: float
    respiracion_promedio: float
    temperatura_promedio: float
    pulso_promedio: float