# app/schemas/veterinaria.py (SOLO CLIENTE - BASADO EN TU SQL)
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

# ========================================
# ENUMS EXACTOS DE TU SQL
# ========================================

class EstadoClienteEnum(str, Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"

# ========================================
# SCHEMAS CLIENTE (BASADO EN TU TABLA)
# ========================================

class ClienteBase(BaseModel):
    nombre: str  # VARCHAR(50) NOT NULL
    apellido_paterno: str  # VARCHAR(50) NOT NULL
    apellido_materno: str  # VARCHAR(50) NOT NULL
    dni: str  # CHAR(8) UNIQUE NOT NULL
    telefono: str  # CHAR(9) NOT NULL
    email: EmailStr  # VARCHAR(100) UNIQUE NOT NULL
    direccion: Optional[str] = None  # TEXT
    estado: Optional[EstadoClienteEnum] = None  # ENUM('Activo', 'Inactivo')

    @validator('nombre')
    def validate_nombre(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nombre debe tener al menos 2 caracteres')
        return v.strip()

    @validator('apellido_paterno')
    def validate_apellido_paterno(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Apellido paterno debe tener al menos 2 caracteres')
        return v.strip()

    @validator('apellido_materno')
    def validate_apellido_materno(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Apellido materno debe tener al menos 2 caracteres')
        return v.strip()

    @validator('dni')
    def validate_dni(cls, v):
        if len(v) != 8 or not v.isdigit():
            raise ValueError('DNI debe tener exactamente 8 dígitos numéricos')
        return v

    @validator('telefono')
    def validate_telefono(cls, v):
        if len(v) != 9 or not v.startswith('9') or not v.isdigit():
            raise ValueError('Teléfono debe tener 9 dígitos y empezar con 9')
        return v

class Cliente(ClienteBase):
    id_cliente: int  # INT PRIMARY KEY AUTO_INCREMENT
    fecha_registro: Optional[datetime] = None  # DATETIME DEFAULT CURRENT_TIMESTAMP

    class Config:
        from_attributes = True

class ClienteCreate(ClienteBase):
    """Schema para crear un nuevo cliente"""
    pass

class ClienteUpdate(BaseModel):
    """Schema para actualizar un cliente (campos opcionales)"""
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    estado: Optional[EstadoClienteEnum] = None

# ========================================
# SCHEMAS PARA RESPUESTAS API
# ========================================

class ClienteResponse(BaseModel):
    """Respuesta estándar para operaciones con clientes"""
    success: bool
    message: str
    data: Optional[Cliente] = None

class ClienteListResponse(BaseModel):
    """Respuesta para lista de clientes"""
    success: bool
    message: str
    data: list[Cliente]
    total: int

class ResponseMessage(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    message: str
    status: str = "error"
    details: Optional[dict] = None