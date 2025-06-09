# app/crud/__init__.py

# CRUD Base
from .base_crud import CRUDBase

# CRUD Principales
from .clientes_crud import cliente
from .mascota_crud import mascota
from .veterinario_crud import veterinario

# CRUD Catálogos
from .catalogo_crud import (
    raza, tipo_animal, especialidad, 
    tipo_servicio, servicio, patologia
)

# CRUD Procesos Clínicos
from .consulta_crud import (
    solicitud_atencion, triaje, consulta,
    diagnostico, tratamiento, historial_clinico
)

# CRUD Servicios y Citas
from .cita_crud import (
    servicio_solicitado, cita, resultado_servicio
)

# CRUD Dashboard
from .dashboard_crud import dashboard

__all__ = [
    # Base
    "CRUDBase",
    
    # Principales
    "cliente",
    "mascota", 
    "veterinario",
    
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
    
    # Dashboard
    "dashboard"
]