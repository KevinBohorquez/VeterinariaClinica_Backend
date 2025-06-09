# app/schemas/base_schema.py
from pydantic import BaseModel, validator
from typing import Optional, Any


class BaseResponse(BaseModel):
    """Schema base para respuestas"""

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    """Schema base para respuestas paginadas"""
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema para mensajes de respuesta"""
    message: str
    success: bool = True


def validate_name(name: str) -> str:
    """Validador reutilizable para nombres"""
    if not name or len(name.strip()) < 2:
        raise ValueError('El nombre debe tener al menos 2 caracteres')
    return name.strip().title()