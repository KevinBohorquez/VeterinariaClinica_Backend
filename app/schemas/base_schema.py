# app/schemas/base_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date


class BaseResponse(BaseModel):
    """Schema base para responses"""
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    """Schema para respuestas paginadas"""
    total: int
    page: int
    per_page: int
    total_pages: int


class MessageResponse(BaseModel):
    """Schema para mensajes simples"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Schema para errores"""
    detail: str
    error_code: Optional[str] = None


# Validators comunes
def validate_dni(cls, v):
    if v and (len(v) != 8 or not v.isdigit()):
        raise ValueError('DNI debe tener exactamente 8 dígitos')
    return v


def validate_telefono(cls, v):
    if v and (len(v) != 9 or not v.startswith('9')):
        raise ValueError('Teléfono debe tener 9 dígitos y empezar con 9')
    return v


def validate_name(cls, v):
    if v and len(v.strip()) < 2:
        raise ValueError('Debe tener al menos 2 caracteres')
    return v.strip().title() if v else v