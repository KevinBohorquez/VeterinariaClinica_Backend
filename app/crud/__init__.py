# app/crud/__init__.py (VERSIÓN COMPLETA)

# CRUD Base
from .base_crud import CRUDBase

# CRUD de Usuarios y Autenticación
from .usuario_crud import usuario
from .administrador_crud import administrador
from .auth_crud import auth

# CRUD Principales
from .clientes_crud import cliente
from .mascota_crud import mascota
from .veterinario_crud import veterinario
from .recepcionista_crud import recepcionista

# CRUD Catálogos (Usando los completos)
from .catalogo_crud import (
    raza, tipo_animal, especialidad, 
    tipo_servicio, servicio, patologia
)

# CRUD Procesos Clínicos
from .consulta_crud import (
    solicitud_atencion, triaje, consulta,
    diagnostico, tratamiento
)

# CRUD Servicios y Citas
from .cita_crud import (
    servicio_solicitado, cita, resultado_servicio
)

# CRUD Historial
from .historial_crud import historial_clinico

# CRUD Solicitudes
from .solicitud_crud import solicitud

# CRUD Dashboard
from .dashboard_crud import dashboard

__all__ = [
    # Base
    "CRUDBase",
    
    # Usuarios y Autenticación
    "usuario",
    "administrador", 
    "auth",
    
    # Principales
    "cliente",
    "mascota", 
    "veterinario",
    "recepcionista",
    
    # Catálogos
    "raza",
    "tipo_animal",
    "especialidad",
    "tipo_servicio",
    "servicio",
    "patologia",
    
    # Procesos Clínicos
    "solicitud_atencion",
    "triaje",
    "consulta",
    "diagnostico",
    "tratamiento",
    "historial_clinico",
    
    # Servicios y Citas
    "servicio_solicitado",
    "cita",
    "resultado_servicio",
    
    # Otros
    "solicitud",
    "dashboard"
]